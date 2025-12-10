import React, { useState } from 'react';
import { toast } from 'sonner';
import { importBriefToFlow } from '../services/workspaceService';

const WorkspaceSyncPage = () => {
  const [title, setTitle] = useState('');
  const [outline, setOutline] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setIsSubmitting(true);
    try {
      const parsedOutline = outline ? JSON.parse(outline) : {};
      await importBriefToFlow(title, parsedOutline);
      toast.success('Brief imported to Flow');
      setTitle('');
      setOutline('');
    } catch (error) {
      toast.error(error.response?.data?.detail || error.message || 'Import failed');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="p-6 space-y-4">
      <h1 className="text-3xl font-bold text-white">Workspace Sync</h1>
      <p className="text-gray-400">
        Paste Gemini Agent Builder output or Docs JSON to push a brief into Flow Studio.
      </p>

      <form onSubmit={handleSubmit} className="bg-gray-900/70 border border-gray-800 rounded-2xl p-6 space-y-4">
        <label className="block text-sm text-gray-400">
          Project Title
          <input
            value={title}
            onChange={(event) => setTitle(event.target.value)}
            className="w-full mt-1 rounded-xl bg-gray-950 border border-gray-800 text-white p-3"
            required
          />
        </label>

        <label className="block text-sm text-gray-400">
          Outline JSON
          <textarea
            value={outline}
            onChange={(event) => setOutline(event.target.value)}
            placeholder='{"synopsis":"...", "beats":[{"title":"Opening", "prompt":"..."}]}'
            className="w-full mt-1 rounded-xl bg-gray-950 border border-gray-800 text-white p-3 h-64 font-mono text-xs"
          />
        </label>

        <button
          type="submit"
          disabled={isSubmitting}
          className="px-6 py-3 rounded-xl bg-gradient-to-r from-lime-500 to-emerald-500 text-white font-semibold"
        >
          {isSubmitting ? 'Syncing…' : 'Import to Flow'}
        </button>
      </form>
    </div>
  );
};

export default WorkspaceSyncPage;

