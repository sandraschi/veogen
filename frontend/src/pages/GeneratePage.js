import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  VideoIcon, 
  SparklesIcon, 
  PlayIcon,
  ClockIcon,
  MaximizeIcon,
  HistoryIcon
} from 'lucide-react';
import { toast } from 'sonner';

const VeoStudio = () => {
  const [prompt, setPrompt] = useState('');
  const [duration, setDuration] = useState(5);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedVideo, setGeneratedVideo] = useState(null);
  const [aspectRatio, setAspectRatio] = useState('16:9');

  const handleGenerate = async () => {
    if (!prompt.trim()) return;
    setIsGenerating(true);
    
    try {
      // Calling Veo 3.1 API via Fleet Backend
      const response = await fetch('/api/video/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          prompt, 
          duration,
          aspect_ratio: aspectRatio,
          model_version: '3.1'
        })
      });
      
      const data = await response.json();
      setGeneratedVideo(data.video_url);
      toast.success('Veo 3.1: Video generation initiated');
    } catch (error) {
      toast.error('Video generation failed');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-4xl font-bold premium-gradient">Veo 3.1 Studio</h1>
          <p className="text-slate-400 mt-2">Cinematic Industrial Video • SOTA Continuity • High Fidelity</p>
        </div>
        <div className="flex bg-white/5 p-1 rounded-xl border border-white/10">
          <button className="px-4 py-2 rounded-lg text-sm bg-purple-500/20 text-purple-300 border border-purple-500/30 flex items-center gap-2">
            <HistoryIcon className="w-4 h-4" />
            Project History
          </button>
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-8">
        {/* Input Side */}
        <div className="space-y-6">
          <div className="glass-panel p-6 space-y-6">
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-300 flex items-center gap-2">
                <SparklesIcon className="w-4 h-4 text-purple-400" />
                Scene Description
              </label>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="A cinematic drone shot of a neon-lit futuristic city in the rain..."
                className="glass-input w-full min-h-[150px] resize-none"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-300 flex items-center gap-2">
                  <ClockIcon className="w-4 h-4 text-indigo-400" />
                  Duration
                </label>
                <select 
                  value={duration} 
                  onChange={(e) => setDuration(Number(e.target.value))}
                  className="glass-input w-full"
                >
                  <option value={5}>5 Seconds</option>
                  <option value={10}>10 Seconds</option>
                  <option value={20}>20 Seconds</option>
                  <option value={60}>60 Seconds (Full)</option>
                </select>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-300 flex items-center gap-2">
                  <MaximizeIcon className="w-4 h-4 text-pink-400" />
                  Aspect Ratio
                </label>
                <select 
                  value={aspectRatio} 
                  onChange={(e) => setAspectRatio(e.target.value)}
                  className="glass-input w-full"
                >
                  <option value="16:9">Ultra-Wide (16:9)</option>
                  <option value="9:16">Mobile Hub (9:16)</option>
                  <option value="1:1">Social Hub (1:1)</option>
                </select>
              </div>
            </div>

            <button
              onClick={handleGenerate}
              disabled={isGenerating || !prompt}
              className="glass-button-primary w-full py-4 flex items-center justify-center gap-3 text-lg"
            >
              {isGenerating ? (
                <>
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>Generating Veo 3.1...</span>
                </>
              ) : (
                <>
                  <PlayIcon className="w-5 h-5 fill-current" />
                  <span>Execute Generation</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Output Side */}
        <div className="glass-panel min-h-[500px] flex flex-col items-center justify-center p-4 relative bg-black/40 overflow-hidden">
          {generatedVideo ? (
            <div className="w-full h-full">
              <video 
                src={generatedVideo} 
                className="w-full h-full object-contain rounded-xl"
                controls
                autoPlay
              />
            </div>
          ) : (
            <div className="text-center space-y-4 opacity-30">
              <VideoIcon className="w-16 h-16 mx-auto" />
              <p className="text-lg">Veo 3.1 Output Preview</p>
            </div>
          )}

          {isGenerating && (
            <div className="absolute inset-0 bg-slate-950/80 backdrop-blur-md flex items-center justify-center z-10">
              <div className="text-center space-y-6 max-w-sm px-4">
                <div className="relative w-20 h-20 mx-auto">
                    <div className="absolute inset-0 border-4 border-purple-500/20 rounded-full" />
                    <div className="absolute inset-0 border-4 border-t-purple-500 rounded-full animate-spin" />
                </div>
                <div className="space-y-2">
                  <h3 className="text-xl font-bold premium-gradient">Rendering Vision</h3>
                  <p className="text-sm text-slate-400">Synthesizing frames with cinematic continuity tokens...</p>
                </div>
                <div className="w-full bg-white/10 rounded-full h-1.5">
                  <motion.div 
                    className="bg-purple-500 h-full rounded-full shadow-[0_0_10px_rgba(168,85,247,0.5)]"
                    initial={{ width: 0 }}
                    animate={{ width: "100%" }}
                    transition={{ duration: 15, repeat: Infinity }}
                  />
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default VeoStudio;
鼓
