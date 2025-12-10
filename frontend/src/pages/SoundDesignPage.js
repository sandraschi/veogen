import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { toast } from 'sonner';
import { generateSoundEffect } from '../services/soundDesignService';

const SoundDesignPage = () => {
  const [form, setForm] = useState({
    prompt: '',
    category: 'ambience',
    duration_seconds: 15,
    loop: true,
    bpm: 100,
    intensity: 'medium',
  });
  const [result, setResult] = useState(null);

  const mutation = useMutation(generateSoundEffect, {
    onSuccess: (data) => {
      setResult(data);
      toast.success('Sound effect generated');
    },
    onError: (error) => toast.error(error.response?.data?.detail || 'AudioFX failed'),
  });

  const handleChange = (event) => {
    const { name, value, type, checked } = event.target;
    setForm((prev) => ({ ...prev, [name]: type === 'checkbox' ? checked : value }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    mutation.mutate({
      ...form,
      duration_seconds: Number(form.duration_seconds),
      bpm: Number(form.bpm),
    });
  };

  return (
    <div className="p-6 space-y-6">
      <header>
        <h1 className="text-3xl font-bold text-white">Sound Design</h1>
        <p className="text-gray-400">
          Generate AudioFX loops that match your Flow scenes or Lyria cues.
        </p>
      </header>

      <form
        onSubmit={handleSubmit}
        className="bg-gray-900/80 border border-gray-800 rounded-2xl p-6 grid grid-cols-1 lg:grid-cols-2 gap-6"
      >
        <div className="space-y-4">
          <label className="block text-sm text-gray-400">
            Prompt
            <textarea
              name="prompt"
              value={form.prompt}
              onChange={handleChange}
              placeholder="Describe the ambience, instrumentation, emotion..."
              className="w-full mt-1 rounded-xl bg-gray-950 border border-gray-800 text-white p-3 h-28"
              required
            />
          </label>

          <label className="block text-sm text-gray-400">
            Category
            <select
              name="category"
              value={form.category}
              onChange={handleChange}
              className="w-full mt-1 rounded-xl bg-gray-950 border border-gray-800 text-white p-3"
            >
              {['ambience', 'foley', 'ui', 'creature', 'sci-fi'].map((option) => (
                <option value={option} key={option}>
                  {option}
                </option>
              ))}
            </select>
          </label>

          <label className="block text-sm text-gray-400">
            Duration (seconds)
            <input
              type="number"
              name="duration_seconds"
              value={form.duration_seconds}
              onChange={handleChange}
              className="w-full mt-1 rounded-xl bg-gray-950 border border-gray-800 text-white p-3"
              min={5}
              max={60}
            />
          </label>

          <label className="flex items-center gap-2 text-sm text-gray-400">
            <input type="checkbox" name="loop" checked={form.loop} onChange={handleChange} />
            Loop friendly output
          </label>
        </div>

        <div className="space-y-4">
          <label className="block text-sm text-gray-400">
            BPM (for Lyria sync)
            <input
              type="number"
              name="bpm"
              value={form.bpm}
              onChange={handleChange}
              className="w-full mt-1 rounded-xl bg-gray-950 border border-gray-800 text-white p-3"
              min={40}
              max={200}
            />
          </label>

          <label className="block text-sm text-gray-400">
            Intensity
            <select
              name="intensity"
              value={form.intensity}
              onChange={handleChange}
              className="w-full mt-1 rounded-xl bg-gray-950 border border-gray-800 text-white p-3"
            >
              {['low', 'medium', 'high'].map((option) => (
                <option value={option} key={option}>
                  {option}
                </option>
              ))}
            </select>
          </label>

          <button
            type="submit"
            disabled={mutation.isLoading}
            className="w-full mt-6 py-3 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-500 text-white font-semibold"
          >
            {mutation.isLoading ? 'Generating...' : 'Generate Sound Effect'}
          </button>
        </div>
      </form>

      {result && (
        <div className="bg-gray-900/70 border border-gray-800 rounded-2xl p-6">
          <h2 className="text-white font-semibold mb-3">Latest Output</h2>
          <audio controls src={result.audio_data || result.file} className="w-full mb-3" />
          <p className="text-xs text-gray-500">SynthID hash: {result.synthid_hash || 'pending'}</p>
        </div>
      )}
    </div>
  );
};

export default SoundDesignPage;

