"""Movie production workflow: LLM script -> Veo clips -> TTS narration -> Lyria score -> ffmpeg.

Two phases, so nothing paid happens by accident:

1. plan    - the selected LLM (Settings -> Text AI) writes a structured script
             (title / visual prompt / narration per scene); a priced estimate is attached.
             Costs one text call. Status ends at "planned".
2. produce - requires confirm_cost=True. Per scene: one Veo 3.1 clip (4/6/8 s, native
             audio), optional Gemini TTS narration; one Lyria track for the whole film;
             then a single ffmpeg pass concatenates the clips and mixes narration and
             music over Veo's own audio.

State is one JSON file per production under OUTPUT_DIR/movies/<id>/ so status survives
a restart (a production that was running is marked "interrupted").

API references (checked 2026-10-13): ai.google.dev/gemini-api/docs/veo,
.../speech-generation, .../music-generation, .../pricing.
"""

from __future__ import annotations

import asyncio
import base64
import json
import logging
import os
import re
import shutil
import subprocess
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from app.config import settings
from app.services import llm_providers

logger = logging.getLogger(__name__)

# USD, paid tier, from https://ai.google.dev/gemini-api/docs/pricing (2026-10-13).
VEO_USD_PER_SECOND = {
    "standard": {"720p": 0.40, "1080p": 0.40},
    "lite": {"720p": 0.05, "1080p": 0.08},
}
LYRIA_USD = {"full": 0.08, "clip": 0.04}
TTS_USD_PER_M_AUDIO_TOKENS = 9.00  # gemini-3.8-flash-tts output, through 2026-12-31
AUDIO_TOKENS_PER_SECOND = 32  # Gemini audio tokenization rate; TTS estimate is approximate

TERMINAL = {"planned", "completed", "failed", "cancelled", "interrupted"}
RUNNING = {"scripting", "generating_clips", "narrating", "scoring", "stitching"}
VEO_POLL_SECONDS = 10
VEO_TIMEOUT_SECONDS = 900

_tasks: Dict[str, asyncio.Task] = {}
_cancelled: set[str] = set()


# --- google client (overridable in tests) -----------------------------------


def _default_client():
    from google import genai

    key = llm_providers.get_key("google")
    if not key:
        raise RuntimeError("No Gemini API key configured (Settings -> Text AI -> Google, or GEMINI_API_KEY)")
    return genai.Client(api_key=key)


client_factory: Callable[[], Any] = _default_client


# --- storage ----------------------------------------------------------------


def movies_dir() -> Path:
    path = Path(settings.OUTPUT_DIR).resolve() / "movies"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _path(pid: str) -> Path:
    if not re.fullmatch(r"[0-9a-f]{12}", pid or ""):
        raise KeyError(pid)
    return movies_dir() / pid / "production.json"


def load(pid: str) -> Dict[str, Any]:
    path = _path(pid)
    if not path.is_file():
        raise KeyError(pid)
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("status") in RUNNING and pid not in _tasks:
        data["status"] = "interrupted"
        data["error"] = data.get("error") or "Server restarted while this production was running."
    return data


def save(prod: Dict[str, Any]) -> None:
    prod["updated_at"] = _now()
    path = _path(prod["id"])
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(prod, indent=2), encoding="utf-8")
    os.replace(tmp, path)


def list_productions() -> List[Dict[str, Any]]:
    out = []
    for p in sorted(movies_dir().glob("*/production.json"), key=lambda f: f.stat().st_mtime, reverse=True):
        try:
            prod = load(p.parent.name)
        except (KeyError, ValueError, OSError):
            continue
        out.append({k: prod.get(k) for k in ("id", "title", "status", "progress", "step", "created_at", "estimate")})
    return out


def _event(prod: Dict[str, Any], step: str, progress: int, message: str) -> None:
    prod["step"] = step
    prod["progress"] = progress
    prod.setdefault("events", []).append({"at": _now(), "step": step, "message": message})
    logger.info("movie %s [%s] %s", prod["id"], step, message)
    save(prod)


# --- estimate ---------------------------------------------------------------


def estimate(
    scene_count: int,
    clip_seconds: int,
    tier: str,
    resolution: str,
    narration: bool,
    music: bool,
) -> Dict[str, Any]:
    seconds = scene_count * clip_seconds
    veo = seconds * VEO_USD_PER_SECOND[tier][resolution]
    music_usd = (LYRIA_USD["clip"] if seconds <= 30 else LYRIA_USD["full"]) if music else 0.0
    tts = seconds * AUDIO_TOKENS_PER_SECOND * TTS_USD_PER_M_AUDIO_TOKENS / 1_000_000 if narration else 0.0
    return {
        "currency": "USD",
        "film_seconds": seconds,
        "veo": round(veo, 2),
        "music": round(music_usd, 2),
        "narration": round(tts, 3),
        "total": round(veo + music_usd + tts, 2),
        "note": "Google paid-tier list prices (2026-10-13); narration is approximate; script text call not included.",
    }


# --- script -----------------------------------------------------------------


def _script_prompt(prod: Dict[str, Any]) -> tuple[str, str]:
    system = (
        "You are a film director writing shot lists for an AI video model (Veo). "
        "Answer with JSON only, no prose and no code fences."
    )
    narration_rule = (
        f"narration: one spoken sentence for this scene, at most {prod['clip_seconds'] * 2 + 2} words"
        if prod["narration"]
        else 'narration: ""'
    )
    prompt = (
        f"Title: {prod['title']}\nConcept: {prod['concept']}\nVisual style: {prod['style']}\n"
        f"Scenes: exactly {prod['scene_count']}, each a single {prod['clip_seconds']}-second shot.\n\n"
        "Return this JSON object:\n"
        '{"synopsis": "...", "music_prompt": "one line describing the score", "scenes": [\n'
        '  {"title": "...", "description": "...", "visual_prompt": "...", "narration": "..."}\n]}\n\n'
        "visual_prompt: a self-contained Veo prompt (subject, action, setting, camera, lighting, style); "
        "repeat recurring characters' appearance in every scene so they stay consistent.\n"
        f"{narration_rule}."
    )
    return system, prompt


def parse_script(text: str, scene_count: int) -> Dict[str, Any]:
    """Extract the JSON script from an LLM answer. Raises ValueError when unusable."""
    cleaned = re.sub(r"^```(?:json)?|```$", "", (text or "").strip(), flags=re.MULTILINE).strip()
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("The LLM answer contained no JSON object")
    data = json.loads(cleaned[start : end + 1])
    scenes = [s for s in data.get("scenes") or [] if isinstance(s, dict) and str(s.get("visual_prompt", "")).strip()]
    if not scenes:
        raise ValueError("The script has no scenes with a visual_prompt")
    scenes = scenes[:scene_count]
    return {
        "synopsis": str(data.get("synopsis", "")),
        "music_prompt": str(data.get("music_prompt", "")),
        "scenes": [
            {
                "index": i,
                "title": str(s.get("title", f"Scene {i + 1}")),
                "description": str(s.get("description", "")),
                "visual_prompt": str(s["visual_prompt"]).strip(),
                "narration": str(s.get("narration", "")).strip(),
                "status": "pending",
            }
            for i, s in enumerate(scenes)
        ],
    }


# --- create / run -----------------------------------------------------------


def create(req: Dict[str, Any]) -> Dict[str, Any]:
    pid = uuid.uuid4().hex[:12]
    prod = {
        "id": pid,
        "title": req["title"],
        "concept": req["concept"],
        "style": req.get("style", "cinematic"),
        "scene_count": int(req.get("scene_count", 4)),
        "clip_seconds": int(req.get("clip_seconds", 8)),
        "tier": req.get("tier", "lite"),
        "resolution": req.get("resolution", "720p"),
        "aspect_ratio": req.get("aspect_ratio", "16:9"),
        "narration": bool(req.get("narration", True)),
        "voice": req.get("voice", "Kore"),
        "music": bool(req.get("music", True)),
        "status": "queued",
        "progress": 0,
        "step": "queued",
        "created_at": _now(),
        "scenes": [],
        "video_path": None,
        "error": None,
        "events": [],
    }
    prod["estimate"] = estimate(
        prod["scene_count"], prod["clip_seconds"], prod["tier"], prod["resolution"], prod["narration"], prod["music"]
    )
    save(prod)
    return prod


def start(pid: str, produce: bool) -> Dict[str, Any]:
    """Run planning (and, when produce=True, media generation) in a background task.

    Re-running a planned / failed / interrupted / cancelled production resumes it:
    the script and any clips or narration already on disk are reused.
    """
    prod = load(pid)
    if pid in _tasks and not _tasks[pid].done():
        raise RuntimeError("This production is already running")
    _cancelled.discard(pid)
    task = asyncio.create_task(_run(pid, produce))
    _tasks[pid] = task
    task.add_done_callback(lambda _t: _tasks.pop(pid, None))
    return prod


def cancel(pid: str) -> Dict[str, Any]:
    prod = load(pid)
    if prod["status"] in TERMINAL:
        return prod
    _cancelled.add(pid)
    return prod


class _Cancelled(Exception):
    pass


def _check(pid: str) -> None:
    if pid in _cancelled:
        raise _Cancelled()


async def _run(pid: str, produce: bool) -> None:
    prod = load(pid)
    try:
        if not prod.get("scenes"):
            prod["status"] = "scripting"
            _event(prod, "script", 5, "Writing the script with the selected text model")
            system, prompt = _script_prompt(prod)
            text = await llm_providers.complete_text(prompt, system=system, temperature=0.8, max_tokens=4000)
            prod["script_raw"] = text
            prod.update(parse_script(text, prod["scene_count"]))
            prod["scene_count"] = len(prod["scenes"])
            prod["estimate"] = estimate(
                prod["scene_count"],
                prod["clip_seconds"],
                prod["tier"],
                prod["resolution"],
                prod["narration"],
                prod["music"],
            )
            prod["status"] = "planned"
            _event(
                prod, "planned", 15, f"Script ready: {prod['scene_count']} scenes, est. ${prod['estimate']['total']}"
            )
        if not produce:
            return
        _check(pid)
        await _produce(prod)
    except _Cancelled:
        prod = load(pid)
        prod["status"] = "cancelled"
        _event(prod, "cancelled", prod.get("progress", 0), "Cancelled by user")
    except Exception as e:  # noqa: BLE001 - recorded on the production, never swallowed silently
        logger.exception("movie %s failed", pid)
        prod["status"] = "failed"
        prod["error"] = f"{type(e).__name__}: {e}"
        _event(prod, "failed", prod.get("progress", 0), prod["error"])
    finally:
        _cancelled.discard(pid)


async def _produce(prod: Dict[str, Any]) -> None:
    pid = prod["id"]
    work = movies_dir() / pid
    client = client_factory()
    scenes = prod["scenes"]
    n = len(scenes)

    prod["status"] = "generating_clips"
    for scene in scenes:
        _check(pid)
        i = scene["index"]
        if scene.get("clip_path") and Path(scene["clip_path"]).is_file():
            continue  # resume after a partial run
        _event(prod, "clips", 15 + int(55 * i / n), f"Veo clip {i + 1}/{n}: {scene['title']}")
        clip = work / f"scene_{i + 1:02d}.mp4"
        await _veo_clip(client, prod, scene, clip)
        scene["clip_path"] = str(clip)
        scene["status"] = "clip_ready"
        save(prod)

    if prod["narration"]:
        prod["status"] = "narrating"
        for scene in scenes:
            _check(pid)
            if not scene.get("narration") or (scene.get("narration_path") and Path(scene["narration_path"]).is_file()):
                continue
            _event(prod, "narration", 70 + int(10 * scene["index"] / n), f"Narration {scene['index'] + 1}/{n}")
            wav = work / f"narration_{scene['index'] + 1:02d}.wav"
            await _tts(client, prod, scene["narration"], wav)
            scene["narration_path"] = str(wav)
            save(prod)

    music_path = None
    if prod["music"]:
        _check(pid)
        prod["status"] = "scoring"
        _event(prod, "music", 82, "Lyria score")
        music_path = work / "score.mp3"
        if not music_path.is_file():
            await _lyria(client, prod, music_path)
        prod["music_path"] = str(music_path)

    _check(pid)
    prod["status"] = "stitching"
    _event(prod, "stitch", 90, "ffmpeg: concatenating clips and mixing audio")
    out = work / "movie.mp4"
    await asyncio.to_thread(
        stitch,
        [s["clip_path"] for s in scenes],
        [s.get("narration_path") for s in scenes],
        str(music_path) if music_path else None,
        prod["clip_seconds"],
        str(out),
    )
    prod["video_path"] = str(out)
    prod["status"] = "completed"
    _event(prod, "completed", 100, f"Done: {out.name}")


# --- google media calls -----------------------------------------------------


async def _veo_clip(client, prod: Dict[str, Any], scene: Dict[str, Any], dest: Path) -> None:
    from google.genai import types

    model = settings.VEO_LITE_MODEL if prod["tier"] == "lite" else settings.VEO_MODEL
    prompt = f"{prod['style']} style. {scene['visual_prompt']}"
    config = types.GenerateVideosConfig(
        aspect_ratio=prod["aspect_ratio"],
        resolution=prod["resolution"],
        duration_seconds=prod["clip_seconds"],
        number_of_videos=1,
    )
    op = await asyncio.to_thread(client.models.generate_videos, model=model, prompt=prompt, config=config)
    deadline = time.monotonic() + VEO_TIMEOUT_SECONDS
    while not op.done:
        _check(prod["id"])
        if time.monotonic() > deadline:
            raise TimeoutError(f"Veo did not finish scene {scene['index'] + 1} within {VEO_TIMEOUT_SECONDS}s")
        await asyncio.sleep(VEO_POLL_SECONDS)
        op = await asyncio.to_thread(client.operations.get, op)
    if getattr(op, "error", None):
        raise RuntimeError(f"Veo error on scene {scene['index'] + 1}: {op.error}")
    videos = getattr(getattr(op, "response", None), "generated_videos", None) or []
    if not videos:
        raise RuntimeError(f"Veo returned no video for scene {scene['index'] + 1} (filtered or empty)")
    await asyncio.to_thread(client.files.download, file=videos[0].video, destination=str(dest))
    if not dest.is_file() or dest.stat().st_size == 0:
        raise RuntimeError(f"Veo clip for scene {scene['index'] + 1} downloaded empty")


async def _tts(client, prod: Dict[str, Any], text: str, dest: Path) -> None:
    interaction = await asyncio.to_thread(
        client.interactions.create,
        model=settings.GEMINI_TTS_MODEL,
        input=[{"type": "user_input", "content": [{"type": "text", "text": text}]}],
        response_format={"type": "audio"},
        generation_config={"speech_config": [{"voice": prod["voice"]}]},
    )
    audio = getattr(interaction, "output_audio", None)
    if not audio or not getattr(audio, "data", None):
        raise RuntimeError("TTS returned no audio")
    dest.write_bytes(base64.b64decode(audio.data))  # unary TTS returns a complete RIFF/WAV


async def _lyria(client, prod: Dict[str, Any], dest: Path) -> None:
    seconds = prod["scene_count"] * prod["clip_seconds"]
    model = settings.LYRIA_CLIP_MODEL if seconds <= 30 else settings.LYRIA_MODEL
    prompt = prod.get("music_prompt") or f"Instrumental film score for: {prod['concept']}"
    prompt = f"{prompt}. Instrumental, no vocals, about {seconds} seconds, {prod['style']} mood."
    interaction = await asyncio.to_thread(client.interactions.create, model=model, input=prompt)
    audio = getattr(interaction, "output_audio", None)
    if not audio or not getattr(audio, "data", None):
        raise RuntimeError(f"{model} returned no audio")
    dest.write_bytes(base64.b64decode(audio.data))


# --- ffmpeg -----------------------------------------------------------------


def ffmpeg_exe() -> str:
    exe = shutil.which("ffmpeg")
    if not exe:
        raise RuntimeError("ffmpeg not found on PATH (install it, e.g. winget install Gyan.FFmpeg)")
    return exe


def stitch(
    clips: List[str],
    narrations: List[Optional[str]],
    music: Optional[str],
    clip_seconds: int,
    out: str,
) -> str:
    """One ffmpeg pass: concat clips (video + native audio), overlay narration at each
    scene's start, add a looped/trimmed music bed, normalize to H.264/AAC."""
    if not clips:
        raise ValueError("No clips to stitch")
    cmd = [ffmpeg_exe(), "-y", "-hide_banner", "-loglevel", "error"]
    for c in clips:
        cmd += ["-i", c]
    narr = [(i, p) for i, p in enumerate(narrations) if p]
    for _i, p in narr:
        cmd += ["-i", p]
    if music:
        cmd += ["-stream_loop", "-1", "-i", music]

    n = len(clips)
    parts = [
        f"[{i}:v]scale=trunc(iw/2)*2:trunc(ih/2)*2,setsar=1,fps=24[v{i}];"
        f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo[a{i}];"
        for i in range(n)
    ]
    chain = "".join(f"[v{i}][a{i}]" for i in range(n))
    graph = "".join(parts) + f"{chain}concat=n={n}:v=1:a=1[vout][base];"
    total = n * clip_seconds
    mix = ["[base]"]
    if narr:
        graph += "[base]volume=0.55[basel];"
        mix = ["[basel]"]
        for k, (scene_idx, _p) in enumerate(narr):
            delay = scene_idx * clip_seconds * 1000
            graph += (
                f"[{n + k}:a]aresample=48000,aformat=channel_layouts=stereo,adelay={delay}|{delay},volume=1.4[n{k}];"
            )
            mix.append(f"[n{k}]")
    if music:
        m = n + len(narr)
        graph += (
            f"[{m}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{total},"
            f"afade=t=out:st={max(total - 2, 0)}:d=2,volume=0.25[mus];"
        )
        mix.append("[mus]")
    if len(mix) > 1:
        graph += "".join(mix) + f"amix=inputs={len(mix)}:duration=first:normalize=0[aout]"
    else:
        graph = graph.rstrip(";").replace("[base]", "[aout]")

    cmd += ["-filter_complex", graph, "-map", "[vout]", "-map", "[aout]"]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p"]
    cmd += ["-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {proc.stderr.strip()[-800:]}")
    return out
