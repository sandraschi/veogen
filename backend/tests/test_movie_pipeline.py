"""Movie production workflow, offline: fake Google client, real ffmpeg on synthetic clips."""

import asyncio
import base64
import json
import shutil
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.services import llm_providers
from app.services import movie_pipeline as mp

FFMPEG = shutil.which("ffmpeg")
needs_ffmpeg = pytest.mark.skipif(FFMPEG is None, reason="ffmpeg not on PATH")


def _lavfi(path: Path, seconds: int, color: str = "blue", tone: int = 440, video: bool = True) -> Path:
    if video:
        args = ["-f", "lavfi", "-i", f"color=c={color}:s=320x180:r=24:d={seconds}"]
        args += ["-f", "lavfi", "-i", f"sine=frequency={tone}:duration={seconds}"]
        args += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest"]
    else:
        args = ["-f", "lavfi", "-i", f"sine=frequency={tone}:duration={seconds}"]
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", *args, str(path)], check=True)
    return path


def _duration(path: str) -> float:
    probe = shutil.which("ffprobe")
    out = subprocess.run(
        [probe, "-v", "error", "-show_entries", "format=duration", "-of", "json", path],
        capture_output=True,
        text=True,
        check=True,
    )
    return float(json.loads(out.stdout)["format"]["duration"])


@pytest.fixture(autouse=True)
def tmp_outputs(tmp_path, monkeypatch):
    monkeypatch.setattr(mp.settings, "OUTPUT_DIR", str(tmp_path / "outputs"))
    monkeypatch.setenv("VEOGEN_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setattr(mp, "VEO_POLL_SECONDS", 0)
    return tmp_path


def test_estimate_uses_list_prices():
    e = mp.estimate(4, 8, "lite", "720p", narration=False, music=True)
    assert e["film_seconds"] == 32 and e["veo"] == 1.6 and e["music"] == 0.08 and e["total"] == 1.68
    assert mp.estimate(2, 8, "standard", "1080p", False, False)["veo"] == 6.4
    assert mp.estimate(3, 6, "lite", "720p", False, True)["music"] == 0.04  # <= 30 s -> clip model


def test_parse_script_accepts_fenced_json_and_rejects_garbage():
    text = '```json\n{"synopsis": "s", "music_prompt": "m", "scenes": [{"title": "A", "visual_prompt": "a cat"}, {"visual_prompt": "a dog", "narration": "Woof."}]}\n```'
    data = mp.parse_script(text, 5)
    assert [s["visual_prompt"] for s in data["scenes"]] == ["a cat", "a dog"]
    assert data["scenes"][1]["narration"] == "Woof." and data["music_prompt"] == "m"
    with pytest.raises(ValueError):
        mp.parse_script("Sorry, I cannot help with that.", 3)
    with pytest.raises(ValueError):
        mp.parse_script('{"scenes": [{"title": "no prompt"}]}', 3)


@needs_ffmpeg
def test_stitch_concats_and_mixes(tmp_path):
    clips = [str(_lavfi(tmp_path / f"c{i}.mp4", 2, c, 300 + 100 * i)) for i, c in enumerate(["red", "green", "blue"])]
    narr = [
        str(_lavfi(tmp_path / "n0.wav", 1, tone=800, video=False)),
        None,
        str(_lavfi(tmp_path / "n2.wav", 1, tone=900, video=False)),
    ]
    music = str(_lavfi(tmp_path / "m.mp3", 1, tone=200, video=False))  # shorter than film: must loop
    out = mp.stitch(clips, narr, music, 2, str(tmp_path / "movie.mp4"))
    assert Path(out).stat().st_size > 1000
    assert 5.5 <= _duration(out) <= 6.6


@needs_ffmpeg
def test_stitch_without_narration_or_music(tmp_path):
    clips = [str(_lavfi(tmp_path / f"c{i}.mp4", 2)) for i in range(2)]
    out = mp.stitch(clips, [None, None], None, 2, str(tmp_path / "plain.mp4"))
    assert 3.5 <= _duration(out) <= 4.6


class FakeClient:
    """Mimics google.genai.Client for generate_videos / operations / files / interactions."""

    def __init__(self, tmp_path: Path):
        self.tmp = tmp_path
        self.calls = {"veo": [], "tts": [], "lyria": []}
        self.models = SimpleNamespace(generate_videos=self._generate_videos)
        self.operations = SimpleNamespace(get=self._get)
        self.files = SimpleNamespace(download=self._download)
        self.interactions = SimpleNamespace(create=self._interaction)

    def _generate_videos(self, model, prompt, config):
        self.calls["veo"].append((model, prompt, config.duration_seconds))
        return SimpleNamespace(done=False, n=len(self.calls["veo"]), seconds=config.duration_seconds)

    def _get(self, op):
        video = SimpleNamespace(video=(op.n, op.seconds))
        return SimpleNamespace(done=True, error=None, response=SimpleNamespace(generated_videos=[video]), n=op.n)

    def _download(self, file, destination):
        n, seconds = file
        _lavfi(Path(destination), seconds, tone=300 + 50 * n)

    def _interaction(self, model, input, **kwargs):
        kind = "tts" if "tts" in model else "lyria"
        self.calls[kind].append(model)
        wav = _lavfi(self.tmp / f"{kind}{len(self.calls[kind])}.wav", 1, tone=700, video=False)
        return SimpleNamespace(output_audio=SimpleNamespace(data=base64.b64encode(wav.read_bytes()).decode()))


SCRIPT = json.dumps(
    {
        "synopsis": "A fox at dawn.",
        "music_prompt": "soft piano",
        "scenes": [
            {"title": "Wake", "visual_prompt": "a red fox wakes in mist", "narration": "Morning comes."},
            {"title": "Run", "visual_prompt": "the red fox runs across a field", "narration": ""},
        ],
    }
)


async def _drain():
    while mp._tasks:
        await asyncio.sleep(0.05)


@needs_ffmpeg
def test_plan_then_produce_end_to_end(tmp_path, monkeypatch):
    async def fake_complete(prompt, **kwargs):
        assert "exactly 2" in prompt
        return SCRIPT

    monkeypatch.setattr(llm_providers, "complete_text", fake_complete)
    fake = FakeClient(tmp_path)
    monkeypatch.setattr(mp, "client_factory", lambda: fake)

    async def scenario():
        prod = mp.create({"title": "Fox", "concept": "a fox greets the day", "scene_count": 2, "clip_seconds": 4})
        mp.start(prod["id"], produce=False)
        await _drain()
        planned = mp.load(prod["id"])
        assert planned["status"] == "planned" and len(planned["scenes"]) == 2
        assert fake.calls["veo"] == []  # planning never touches paid media
        mp.start(prod["id"], produce=True)
        await _drain()
        return mp.load(prod["id"])

    done = asyncio.run(scenario())
    assert done["status"] == "completed", done.get("error")
    assert done["progress"] == 100
    assert [c[0] for c in fake.calls["veo"]] == [mp.settings.VEO_LITE_MODEL] * 2
    assert all(c[2] == 4 for c in fake.calls["veo"])
    assert fake.calls["tts"] == [mp.settings.GEMINI_TTS_MODEL]  # scene 2 has no narration
    assert fake.calls["lyria"] == [mp.settings.LYRIA_CLIP_MODEL]  # 8 s film -> clip model
    assert Path(done["video_path"]).is_file() and 7.5 <= _duration(done["video_path"]) <= 8.6


def test_unparseable_script_fails_honestly(monkeypatch):
    async def fake_complete(prompt, **kwargs):
        return "I would love to help, but here is a poem instead."

    monkeypatch.setattr(llm_providers, "complete_text", fake_complete)

    async def scenario():
        prod = mp.create({"title": "X", "concept": "y" * 30, "scene_count": 3})
        mp.start(prod["id"], produce=False)
        await _drain()
        return mp.load(prod["id"])

    prod = asyncio.run(scenario())
    assert prod["status"] == "failed" and "JSON" in prod["error"]
    assert prod["scenes"] == []


def test_cancel_stops_before_next_clip(tmp_path, monkeypatch):
    async def fake_complete(prompt, **kwargs):
        return SCRIPT

    monkeypatch.setattr(llm_providers, "complete_text", fake_complete)
    fake = FakeClient(tmp_path)

    def gen_then_cancel(model, prompt, config):
        mp._cancelled.add(prod_id[0])
        return FakeClient._generate_videos(fake, model, prompt, config)

    fake.models = SimpleNamespace(generate_videos=gen_then_cancel)
    monkeypatch.setattr(mp, "client_factory", lambda: fake)
    prod_id = []

    async def scenario():
        prod = mp.create({"title": "Fox", "concept": "a fox greets the day", "scene_count": 2, "clip_seconds": 4})
        prod_id.append(prod["id"])
        mp.start(prod["id"], produce=True)
        await _drain()
        return mp.load(prod["id"])

    prod = asyncio.run(scenario())
    assert prod["status"] == "cancelled"
    assert len(fake.calls["veo"]) == 1
