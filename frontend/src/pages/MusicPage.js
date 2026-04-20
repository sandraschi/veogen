import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  MusicIcon, 
  SparklesIcon, 
  PlayIcon,
  PauseIcon,
  DownloadIcon,
  WavesIcon
} from 'lucide-react';
import { toast } from 'sonner';

const LyriaStudio = () => {
  const [prompt, setPrompt] = useState('');
  const [genre, setGenre] = useState('ambient');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedAudio, setGeneratedAudio] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);

  const handleGenerate = async () => {
    if (!prompt.trim()) return;
    setIsGenerating(true);
    
    try {
      const response = await fetch('/api/music/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          prompt, 
          genre,
          model: 'lyria-3'
        })
      });
      
      const data = await response.json();
      setGeneratedAudio(data.audio_url);
      toast.success('Lyria 3: High-fidelity composition ready');
    } catch (error) {
      toast.error('Music generation failed');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold premium-gradient">Lyria 3 Studio</h1>
        <p className="text-slate-400 mt-2">SOTA Composition • High-Fidelity Audio • Genre Mastery</p>
      </div>

      <div className="grid lg:grid-cols-2 gap-8">
        {/* Controls */}
        <div className="space-y-6">
          <div className="glass-panel p-6 space-y-6">
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-300 flex items-center gap-2">
                <SparklesIcon className="w-4 h-4 text-purple-400" />
                Musical Concept
              </label>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Lofi beats with a melancholic piano melody and rainy atmosphere..."
                className="glass-input w-full min-h-[120px] resize-none"
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-300 flex items-center gap-2">
                <MusicIcon className="w-4 h-4 text-indigo-400" />
                Genre Preset
              </label>
              <select 
                value={genre} 
                onChange={(e) => setGenre(e.target.value)}
                className="glass-input w-full"
              >
                <option value="ambient">Ambient / Atmospheric</option>
                <option value="lofi">Lofi / Chill</option>
                <option value="cinematic">Cinematic Orchestral</option>
                <option value="synthwave">80s Synthwave</option>
                <option value="techno">Industrial Techno</option>
              </select>
            </div>

            <button
              onClick={handleGenerate}
              disabled={isGenerating || !prompt}
              className="glass-button-primary w-full py-4 flex items-center justify-center gap-3"
            >
              {isGenerating ? (
                <>
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>Composing with Lyria 3...</span>
                </>
              ) : (
                <>
                  <WavesIcon className="w-5 h-5" />
                  <span>Generate Full Track</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Playback Area */}
        <div className="glass-panel min-h-[400px] flex flex-col items-center justify-center p-8 relative">
          {generatedAudio ? (
            <div className="w-full space-y-12">
              {/* Visualizer animation placeholder */}
              <div className="flex items-center justify-center gap-1.5 h-32">
                {[...Array(20)].map((_, i) => (
                  <motion.div
                    key={i}
                    className="w-1.5 bg-gradient-to-t from-purple-500 to-pink-500 rounded-full"
                    animate={{ 
                      height: isPlaying ? [20, 80, 40, 100, 30] : 10 
                    }}
                    transition={{ 
                      repeat: Infinity, 
                      duration: 0.8, 
                      delay: i * 0.05,
                      ease: "easeInOut"
                    }}
                  />
                ))}
              </div>

              <div className="flex flex-col items-center gap-6">
                <button 
                  onClick={() => setIsPlaying(!isPlaying)}
                  className="w-20 h-20 rounded-full bg-white/10 border border-white/20 flex items-center justify-center hover:bg-white/20 transition-all active:scale-95"
                >
                  {isPlaying ? <PauseIcon className="w-8 h-8" /> : <PlayIcon className="w-8 h-8 ml-1" />}
                </button>
                
                <div className="w-full space-y-2">
                  <div className="flex justify-between text-xs text-slate-400">
                    <span>0:12</span>
                    <span>0:30</span>
                  </div>
                  <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
                    <motion.div 
                      className="bg-purple-500 h-full w-1/3"
                      animate={{ width: isPlaying ? "100%" : "33%" }}
                      transition={{ duration: 30, ease: "linear" }}
                    />
                  </div>
                </div>

                <button className="glass-button-secondary flex items-center gap-2">
                  <DownloadIcon className="w-4 h-4" />
                  Download WAV
                </button>
              </div>
            </div>
          ) : (
            <div className="text-center space-y-4 opacity-30">
              <MusicIcon className="w-16 h-16 mx-auto" />
              <p className="text-lg">Lyria 3 Composition Preview</p>
            </div>
          )}

          {isGenerating && (
            <div className="absolute inset-0 bg-slate-950/80 backdrop-blur-md flex items-center justify-center z-10 rounded-2xl">
              <div className="text-center space-y-4">
                <div className="w-16 h-16 border-4 border-purple-500/20 border-t-purple-500 rounded-full animate-spin mx-auto" />
                <p className="premium-gradient font-medium">Harmonizing tokens...</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default LyriaStudio;
鼓