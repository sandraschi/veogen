import React, { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import { toast } from 'sonner';
import { critiquePrompt, startPromptCoachSession } from '../../services/promptCoachService';

const PromptCoachWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [prompt, setPrompt] = useState('');
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (!isOpen || sessionId) return;
    startPromptCoachSession()
      .then((id) => setSessionId(id))
      .catch(() => toast.error('Prompt coach unavailable'));
  }, [isOpen, sessionId]);

  const handleCritique = async () => {
    if (!prompt.trim()) return;
    if (!sessionId) {
      toast.error('Session not ready yet.');
      return;
    }

    setIsLoading(true);
    try {
      const result = await critiquePrompt(sessionId, prompt);
      setMessages((prev) => [
        {
          prompt,
          summary: result.summary,
          recommendations: result.recommendations || [],
          timestamp: new Date().toISOString(),
        },
        ...prev,
      ]);
      setPrompt('');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Critique failed');
    } finally {
      setIsLoading(false);
    }
  };

  return createPortal(
    <div className="fixed bottom-6 right-6 z-50">
      {isOpen && (
        <div className="w-96 bg-gray-900/90 border border-gray-800 rounded-2xl shadow-2xl p-4 mb-3 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-white font-semibold">Prompt Coach</p>
              <p className="text-xs text-gray-500">{sessionId ? 'Live' : 'Initializing...'}</p>
            </div>
            <button
              type="button"
              className="text-gray-400 hover:text-white"
              onClick={() => setIsOpen(false)}
              aria-label="Close prompt coach"
            >
              ✕
            </button>
          </div>

          <textarea
            value={prompt}
            onChange={(event) => setPrompt(event.target.value)}
            placeholder="Paste your Veo/Nano Banana/Lyria prompt…"
            className="w-full bg-gray-950 border border-gray-800 rounded-xl text-white p-3 h-28 text-sm"
          />
          <button
            type="button"
            onClick={handleCritique}
            disabled={isLoading}
            className="w-full py-2 rounded-xl bg-gradient-to-r from-purple-500 to-pink-500 text-white text-sm font-semibold"
          >
            {isLoading ? 'Reviewing…' : 'Critique Prompt'}
          </button>

          <div className="space-y-3 max-h-48 overflow-y-auto">
            {messages.map((message, index) => (
              <div
                // biome-ignore lint/suspicious/noArrayIndexKey: append-only transcript, messages carry no id and are never reordered
                key={index}
                className="bg-gray-950/60 border border-gray-800 rounded-xl p-3 text-xs text-gray-300 space-y-2"
              >
                <p className="font-semibold text-white">{message.summary}</p>
                <ul className="list-disc list-inside space-y-1">
                  {(message.recommendations || []).map((rec) => (
                    <li key={rec}>{rec}</li>
                  ))}
                </ul>
              </div>
            ))}
            {!messages.length && <p className="text-gray-500 text-xs">No critiques yet. Paste a prompt to begin.</p>}
          </div>
        </div>
      )}

      <button
        type="button"
        className="w-14 h-14 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg flex items-center justify-center"
        onClick={() => setIsOpen((prev) => !prev)}
      >
        ✨
      </button>
    </div>,
    document.body,
  );
};

export default PromptCoachWidget;
