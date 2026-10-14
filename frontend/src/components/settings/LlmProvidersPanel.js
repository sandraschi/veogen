import React, { useCallback, useEffect, useState } from 'react';
import { toast } from 'sonner';

// Local + cloud LLM providers for veogen's text features (chat, movie scripts,
// book, code). Fleet contract: WEBAPP_SOTA_STANDARDS.md VI.10. Everything goes
// through the backend proxy; keys are write-only and never come back.

const authHeaders = () => {
  const token = localStorage.getItem('token');
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
};

const getJson = async (url, options = {}) => {
  const res = await fetch(url, {
    ...options,
    headers: { ...authHeaders(), ...(options.headers || {}) },
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(body.detail || `HTTP ${res.status}`);
  return body;
};

const statusOf = (p) => {
  if (p.kind === 'local') return p.detected ? ['Detected', 'bg-emerald-500'] : ['Not running', 'bg-gray-500'];
  return p.configured ? ['Key configured', 'bg-emerald-500'] : ['Missing key', 'bg-amber-500'];
};

const LlmProvidersPanel = () => {
  const [providers, setProviders] = useState([]);
  const [selection, setSelection] = useState({ provider: '', model: '' });
  const [models, setModels] = useState({ models: [], source: '' });
  const [keys, setKeys] = useState({});
  const [busy, setBusy] = useState('');

  const load = useCallback(async () => {
    try {
      const [rows, current] = await Promise.all([getJson('/api/llm/providers'), getJson('/api/settings/llm')]);
      setProviders(rows);
      setSelection({ provider: current.provider, model: current.model });
    } catch (e) {
      toast.error(`LLM providers unavailable: ${e.message}`);
    }
  }, []);

  const loadModels = useCallback(async (providerId) => {
    if (!providerId) return;
    try {
      setModels(await getJson(`/api/llm/models?provider=${encodeURIComponent(providerId)}`));
    } catch (e) {
      setModels({ models: [], source: 'none', error: e.message });
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    loadModels(selection.provider);
  }, [selection.provider, loadModels]);

  const saveSelection = async (provider, model) => {
    setBusy('selection');
    try {
      const saved = await getJson('/api/settings/llm', {
        method: 'POST',
        body: JSON.stringify({ provider, model }),
      });
      setSelection({ provider: saved.provider, model: saved.model });
      toast.success(`Text generation now uses ${provider} / ${model}`);
    } catch (e) {
      toast.error(`Could not save selection: ${e.message} (are you logged in?)`);
    } finally {
      setBusy('');
    }
  };

  const saveKey = async (providerId) => {
    const apiKey = (keys[providerId] || '').trim();
    if (!apiKey) return;
    setBusy(`key-${providerId}`);
    try {
      await getJson('/api/settings/llm', {
        method: 'POST',
        body: JSON.stringify({ provider: providerId, api_key: apiKey }),
      });
      setKeys((k) => ({ ...k, [providerId]: '' }));
      toast.success('Key saved');
      await load();
    } catch (e) {
      toast.error(`Could not save key: ${e.message}`);
    } finally {
      setBusy('');
    }
  };

  const clearKey = async (providerId) => {
    setBusy(`key-${providerId}`);
    try {
      const res = await getJson(`/api/settings/llm/key?provider=${encodeURIComponent(providerId)}`, {
        method: 'DELETE',
      });
      toast.success(res.removed ? 'Stored key removed' : 'No stored key (an environment variable may still be set)');
      await load();
    } catch (e) {
      toast.error(`Could not clear key: ${e.message}`);
    } finally {
      setBusy('');
    }
  };

  const testProvider = async (providerId) => {
    setBusy(`test-${providerId}`);
    try {
      const res = await getJson(`/api/llm/models?provider=${encodeURIComponent(providerId)}`);
      if (res.error) toast.error(res.error);
      else if (res.key_missing) toast.warning('No key saved - showing the curated model list only');
      else if (res.source === 'none') toast.error('Not reachable - is the engine running?');
      else toast.success(`OK: ${res.models.length} models (${res.source})`);
    } catch (e) {
      toast.error(e.message);
    } finally {
      setBusy('');
    }
  };

  const usable = (p) => (p.kind === 'local' ? p.detected : p.configured);

  return (
    <div
      className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10"
      data-testid="llm-providers-panel"
    >
      <h2 className="text-xl font-semibold text-white mb-1">Text AI (local + cloud)</h2>
      <p className="text-sm text-gray-400 mb-4">
        Chat, movie scripts, book and code use this model. Video, image and music always use Google (Veo, Nano Banana,
        Lyria).
      </p>

      <div className="grid md:grid-cols-2 gap-3 mb-6">
        <label className="text-sm text-gray-300">
          Provider
          <select
            data-testid="llm-provider-select"
            className="mt-1 w-full bg-gray-900 border border-white/10 rounded-lg p-2 text-white"
            value={selection.provider}
            onChange={(e) => setSelection({ provider: e.target.value, model: '' })}
          >
            {providers.map((p) => (
              <option key={p.id} value={p.id} disabled={!usable(p)}>
                {p.label} {usable(p) ? '' : `(${statusOf(p)[0].toLowerCase()})`}
              </option>
            ))}
          </select>
        </label>
        <label className="text-sm text-gray-300">
          Model {models.source && <span className="text-xs text-gray-500">({models.source})</span>}
          <select
            data-testid="llm-model-select"
            className="mt-1 w-full bg-gray-900 border border-white/10 rounded-lg p-2 text-white"
            value={selection.model}
            onChange={(e) => saveSelection(selection.provider, e.target.value)}
            disabled={busy === 'selection' || models.models.length === 0}
          >
            {!selection.model && <option value="">Choose a model</option>}
            {selection.model && !models.models.includes(selection.model) && (
              <option value={selection.model}>{selection.model}</option>
            )}
            {models.models.map((m) => (
              <option key={m} value={m}>
                {m}
              </option>
            ))}
          </select>
        </label>
      </div>

      <div className="space-y-3">
        {providers.map((p) => {
          const [label, dot] = statusOf(p);
          return (
            <div key={p.id} data-testid={`llm-provider-card-${p.id}`} className="rounded-lg border border-white/10 p-3">
              <div className="flex items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <span className={`w-2 h-2 rounded-full ${dot}`} />
                  <span className="text-white font-medium">{p.label}</span>
                  <span className="text-xs px-2 py-0.5 rounded bg-white/10 text-gray-300">
                    {p.kind === 'local' ? 'Local / free' : 'Cloud / paid'}
                  </span>
                  <span className="text-xs text-gray-400">{label}</span>
                </div>
                <button
                  type="button"
                  data-testid={`llm-test-${p.id}`}
                  className="text-xs px-3 py-1 rounded bg-white/10 hover:bg-white/20 text-white"
                  onClick={() => testProvider(p.id)}
                  disabled={busy === `test-${p.id}`}
                >
                  Test
                </button>
              </div>
              {p.kind === 'cloud' && (
                <div className="mt-2 flex gap-2">
                  <input
                    type="password"
                    data-testid={`llm-key-${p.id}`}
                    autoComplete="off"
                    className="flex-1 bg-gray-900 border border-white/10 rounded p-2 text-sm text-white"
                    placeholder={p.configured ? 'Key configured - paste to replace' : `${p.key_env || 'API key'}`}
                    value={keys[p.id] || ''}
                    onChange={(e) => setKeys((k) => ({ ...k, [p.id]: e.target.value }))}
                  />
                  <button
                    type="button"
                    className="text-xs px-3 rounded bg-blue-600 hover:bg-blue-500 text-white disabled:opacity-50"
                    onClick={() => saveKey(p.id)}
                    disabled={!keys[p.id] || busy === `key-${p.id}`}
                  >
                    Save
                  </button>
                  <button
                    type="button"
                    className="text-xs px-3 rounded bg-white/10 hover:bg-white/20 text-white"
                    onClick={() => clearKey(p.id)}
                    disabled={busy === `key-${p.id}`}
                  >
                    Clear
                  </button>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default LlmProvidersPanel;
