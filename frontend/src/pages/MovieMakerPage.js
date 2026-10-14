import { ArrowDownTrayIcon, FilmIcon, PlayIcon, SparklesIcon, StopIcon } from '@heroicons/react/24/outline';
import { motion } from 'framer-motion';
import React, { useCallback, useEffect, useRef, useState } from 'react';
import { toast } from 'sonner';

// Movie Maker: plan (LLM script + priced estimate) -> review -> produce (Veo clips,
// TTS narration, Lyria score, ffmpeg) with live progress. Backend:
// /api/v1/movie/productions* (see backend/app/services/movie_pipeline.py).

const API = '/api/v1/movie';

const STYLES = [
  ['cinematic', 'Cinematic'],
  ['anime', 'Anime'],
  ['pixar', '3D animated'],
  ['wes-anderson', 'Wes Anderson'],
  ['claymation', 'Claymation'],
  ['documentary', 'Documentary'],
  ['music-video', 'Music video'],
  ['advertisement', 'Commercial'],
];
const VOICES = ['Kore', 'Puck', 'Zephyr', 'Charon', 'Fenrir'];
const RUNNING = ['queued', 'scripting', 'generating_clips', 'narrating', 'scoring', 'stitching'];

const headers = () => {
  const token = localStorage.getItem('token');
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
};

const call = async (path, options = {}) => {
  const res = await fetch(`${API}${path}`, { ...options, headers: headers() });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) {
    const detail = typeof body.detail === 'object' ? body.detail.message : body.detail;
    throw new Error(detail || `HTTP ${res.status}`);
  }
  return body;
};

const DEFAULTS = {
  title: '',
  concept: '',
  style: 'cinematic',
  scene_count: 4,
  clip_seconds: 8,
  tier: 'lite',
  resolution: '720p',
  aspect_ratio: '16:9',
  narration: true,
  voice: 'Kore',
  music: true,
};

const Field = ({ label, children }) => (
  <label className="block text-sm text-gray-300">
    <span className="mb-1 block">{label}</span>
    {children}
  </label>
);

const inputCls = 'w-full bg-gray-900 border border-white/10 rounded-lg p-2 text-white';

const MovieMakerPage = () => {
  const [form, setForm] = useState(DEFAULTS);
  const [estimate, setEstimate] = useState(null);
  const [production, setProduction] = useState(null);
  const [recent, setRecent] = useState([]);
  const [busy, setBusy] = useState(false);
  const poll = useRef(null);

  const set = (key) => (e) => {
    const t = e.target;
    const value =
      t.type === 'checkbox' ? t.checked : t.type === 'number' || key === 'clip_seconds' ? Number(t.value) : t.value;
    setForm((f) => ({ ...f, [key]: value }));
  };

  // live, free estimate
  useEffect(() => {
    const body = {
      ...form,
      title: form.title || 'tmp',
      concept: form.concept.padEnd(20, '.'),
    };
    const id = setTimeout(() => {
      call('/productions/estimate', {
        method: 'POST',
        body: JSON.stringify(body),
      })
        .then(setEstimate)
        .catch(() => setEstimate(null));
    }, 250);
    return () => clearTimeout(id);
  }, [form]);

  const loadRecent = useCallback(() => {
    call('/productions')
      .then(setRecent)
      .catch(() => {});
  }, []);
  useEffect(() => {
    loadRecent();
  }, [loadRecent]);

  const watch = useCallback(
    (id) => {
      clearInterval(poll.current);
      const tick = async () => {
        try {
          const p = await call(`/productions/${id}`);
          setProduction(p);
          if (!RUNNING.includes(p.status)) {
            clearInterval(poll.current);
            loadRecent();
            if (p.status === 'failed') toast.error(p.error || 'Production failed');
            if (p.status === 'completed') toast.success('Your movie is ready');
          }
        } catch (e) {
          clearInterval(poll.current);
          toast.error(e.message);
        }
      };
      tick();
      poll.current = setInterval(tick, 3000);
    },
    [loadRecent],
  );
  useEffect(() => () => clearInterval(poll.current), []);

  const plan = async (e) => {
    e.preventDefault();
    if (form.title.trim().length < 3 || form.concept.trim().length < 20) {
      toast.error('Title needs 3+ characters and the concept 20+');
      return;
    }
    setBusy(true);
    try {
      const p = await call('/productions', {
        method: 'POST',
        body: JSON.stringify({ ...form, produce: false }),
      });
      setProduction(p);
      watch(p.id);
    } catch (err) {
      toast.error(`${err.message} (are you logged in?)`);
    } finally {
      setBusy(false);
    }
  };

  const produce = async () => {
    const total = production?.estimate?.total;
    if (
      !window.confirm(
        `Generate this film with Google Veo, TTS and Lyria for about $${total}? This is billed to your Gemini key.`,
      )
    )
      return;
    setBusy(true);
    try {
      await call(`/productions/${production.id}/produce`, {
        method: 'POST',
        body: JSON.stringify({ confirm_cost: true }),
      });
      watch(production.id);
    } catch (err) {
      toast.error(err.message);
    } finally {
      setBusy(false);
    }
  };

  const cancel = async () => {
    try {
      await call(`/productions/${production.id}/cancel`, { method: 'POST' });
      toast.info('Cancelling before the next paid call');
    } catch (err) {
      toast.error(err.message);
    }
  };

  const running = production && RUNNING.includes(production.status);
  const canProduce =
    production &&
    ['planned', 'failed', 'interrupted', 'cancelled'].includes(production.status) &&
    production.scenes?.length > 0;

  return (
    <div className="max-w-5xl mx-auto space-y-8" data-testid="movie-maker">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="text-center">
        <div className="w-20 h-20 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center mx-auto mb-6">
          <FilmIcon className="w-10 h-10 text-white" />
        </div>
        <h1 className="text-3xl md:text-4xl font-bold text-white mb-2">Movie Maker</h1>
        <p className="text-gray-400 max-w-2xl mx-auto">
          Plan a short film with your text model, review the shot list, then produce it with Veo 3.1 clips, narration
          and a Lyria score.
        </p>
      </motion.div>

      <form
        onSubmit={plan}
        className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10 space-y-4"
        data-testid="movie-form"
      >
        <div className="grid md:grid-cols-2 gap-4">
          <Field label="Title">
            <input
              data-testid="movie-title"
              className={inputCls}
              value={form.title}
              onChange={set('title')}
              maxLength={100}
            />
          </Field>
          <Field label="Style">
            <select className={inputCls} value={form.style} onChange={set('style')}>
              {STYLES.map(([id, name]) => (
                <option key={id} value={id}>
                  {name}
                </option>
              ))}
            </select>
          </Field>
        </div>
        <Field label="Concept">
          <textarea
            data-testid="movie-concept"
            className={`${inputCls} h-24`}
            value={form.concept}
            onChange={set('concept')}
            maxLength={2000}
          />
        </Field>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Field label="Scenes">
            <input
              type="number"
              min={1}
              max={12}
              className={inputCls}
              value={form.scene_count}
              onChange={set('scene_count')}
            />
          </Field>
          <Field label="Seconds per scene">
            <select className={inputCls} value={form.clip_seconds} onChange={set('clip_seconds')}>
              {[4, 6, 8].map((s) => (
                <option key={s} value={s}>
                  {s}s
                </option>
              ))}
            </select>
          </Field>
          <Field label="Veo tier">
            <select className={inputCls} value={form.tier} onChange={set('tier')}>
              <option value="lite">Lite ($0.05/s at 720p)</option>
              <option value="standard">Standard ($0.40/s)</option>
            </select>
          </Field>
          <Field label="Resolution / aspect">
            <div className="flex gap-2">
              <select className={inputCls} value={form.resolution} onChange={set('resolution')}>
                <option value="720p">720p</option>
                <option value="1080p">1080p</option>
              </select>
              <select className={inputCls} value={form.aspect_ratio} onChange={set('aspect_ratio')}>
                <option value="16:9">16:9</option>
                <option value="9:16">9:16</option>
              </select>
            </div>
          </Field>
        </div>
        <div className="flex flex-wrap items-center gap-6 text-sm text-gray-300">
          <label className="flex items-center gap-2">
            <input type="checkbox" checked={form.narration} onChange={set('narration')} /> Narration
          </label>
          {form.narration && (
            <select
              className="bg-gray-900 border border-white/10 rounded p-1 text-white"
              value={form.voice}
              onChange={set('voice')}
            >
              {VOICES.map((v) => (
                <option key={v}>{v}</option>
              ))}
            </select>
          )}
          <label className="flex items-center gap-2">
            <input type="checkbox" checked={form.music} onChange={set('music')} /> Music score
          </label>
          {estimate && (
            <span className="ml-auto text-gray-400" data-testid="movie-estimate">
              {estimate.film_seconds}s film, est.{' '}
              <span className="text-green-400 font-semibold">${estimate.total}</span> (Veo ${estimate.veo}
              {form.music ? `, music $${estimate.music}` : ''})
            </span>
          )}
        </div>
        <button
          type="submit"
          data-testid="movie-plan"
          disabled={busy || running}
          className="w-full py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-semibold rounded-xl disabled:opacity-50 flex items-center justify-center gap-2"
        >
          <SparklesIcon className="w-5 h-5" /> Plan script (uses your text model, no media cost)
        </button>
      </form>

      {production && (
        <div
          className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10 space-y-4"
          data-testid="movie-production"
        >
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-white">{production.title}</h2>
            <span className="text-sm text-gray-400" data-testid="movie-status">
              {production.status} {running ? `- ${production.step}` : ''}
            </span>
          </div>
          <div className="w-full h-2 bg-white/10 rounded">
            <div
              className="h-2 rounded bg-gradient-to-r from-purple-500 to-pink-500 transition-all"
              style={{ width: `${production.progress || 0}%` }}
            />
          </div>
          {production.error && <p className="text-red-400 text-sm">{production.error}</p>}
          {production.synopsis && <p className="text-gray-300 text-sm">{production.synopsis}</p>}

          {production.scenes?.length > 0 && (
            <ol className="space-y-2">
              {production.scenes.map((s) => (
                <li key={s.index} className="rounded-lg border border-white/10 p-3 text-sm">
                  <div className="flex justify-between text-white">
                    <span>
                      {s.index + 1}. {s.title}
                    </span>
                    <span className="text-gray-400">{s.status}</span>
                  </div>
                  <p className="text-gray-400 mt-1">{s.visual_prompt}</p>
                  {s.narration && <p className="text-purple-300 mt-1 italic">"{s.narration}"</p>}
                </li>
              ))}
            </ol>
          )}

          <div className="flex flex-wrap gap-3">
            {canProduce && (
              <button
                type="button"
                data-testid="movie-produce"
                onClick={produce}
                disabled={busy}
                className="px-5 py-2 rounded-lg bg-green-600 hover:bg-green-500 text-white font-medium flex items-center gap-2 disabled:opacity-50"
              >
                <PlayIcon className="w-5 h-5" /> Produce for about ${production.estimate?.total}
              </button>
            )}
            {running && production.status !== 'scripting' && (
              <button
                type="button"
                onClick={cancel}
                className="px-5 py-2 rounded-lg bg-white/10 hover:bg-white/20 text-white flex items-center gap-2"
              >
                <StopIcon className="w-5 h-5" /> Cancel
              </button>
            )}
          </div>

          {production.status === 'completed' && (
            <div className="space-y-2">
              <video
                data-testid="movie-video"
                controls
                className="w-full rounded-lg"
                src={`${API}/productions/${production.id}/video`}
              >
                <track kind="captions" />
              </video>
              <a
                href={`${API}/productions/${production.id}/video`}
                download
                className="inline-flex items-center gap-2 text-purple-300 hover:text-purple-200 text-sm"
              >
                <ArrowDownTrayIcon className="w-4 h-4" /> Download MP4
              </a>
            </div>
          )}

          {production.events?.length > 0 && (
            <details className="text-xs text-gray-500">
              <summary className="cursor-pointer">Log</summary>
              <ul className="mt-2 space-y-1">
                {production.events.map((ev) => (
                  <li key={`${ev.at}-${ev.step}-${ev.message}`}>
                    {ev.at} [{ev.step}] {ev.message}
                  </li>
                ))}
              </ul>
            </details>
          )}
        </div>
      )}

      {recent.length > 0 && (
        <div className="bg-white/5 rounded-xl p-6 border border-white/10" data-testid="movie-recent">
          <h3 className="text-white font-semibold mb-3">Recent productions</h3>
          <ul className="divide-y divide-white/5 text-sm">
            {recent.slice(0, 10).map((p) => (
              <li key={p.id} className="py-2 flex justify-between items-center">
                <button
                  type="button"
                  className="text-left text-purple-300 hover:text-purple-200"
                  onClick={() => watch(p.id)}
                >
                  {p.title}
                </button>
                <span className="text-gray-400">
                  {p.status} {p.estimate ? `- $${p.estimate.total}` : ''}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default MovieMakerPage;
