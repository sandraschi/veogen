import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Image, 
  Sparkles, 
  Download,
  Search,
  CaseSensitive
} from 'lucide-react';
import { toast } from 'sonner';

const ImageStudio = () => {
  const [prompt, setPrompt] = useState('');
  const [textInImage, setTextInImage] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [resultImage, setResultImage] = useState(null);
  const [aspectRatio, setAspectRatio] = useState('1:1');

  const handleGenerate = async () => {
    if (!prompt.trim()) return;
    setIsGenerating(true);
    
    try {
      // Calling Nano Banana 2 API
      const response = await fetch('/api/image/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          prompt, 
          text: textInImage,
          aspect_ratio: aspectRatio,
          search_grounding: true 
        })
      });
      
      const data = await response.json();
      setResultImage(data.image_url);
      toast.success('Nano Banana 2: Image generated with 4K clarity');
    } catch (error) {
      toast.error('Image generation failed');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Hero Section */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-4xl font-bold premium-gradient">Nano Banana 2 Studio</h1>
          <p className="text-slate-400 mt-2">Gemini 3.1 Flash Image • 4K • Text Rendering • Search Grounded</p>
        </div>
        <div className="flex bg-white/5 p-1 rounded-xl border border-white/10">
          {['1:1', '16:9', '9:16'].map(ratio => (
            <button
              key={ratio}
              onClick={() => setAspectRatio(ratio)}
              className={`px-4 py-1.5 rounded-lg text-sm transition-all ${
                aspectRatio === ratio ? 'bg-purple-600 text-white shadow-lg' : 'text-slate-400 hover:text-white'
              }`}
            >
              {ratio}
            </button>
          ))}
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-8">
        {/* Control Panel */}
        <div className="space-y-6">
          <div className="glass-panel p-6 space-y-6">
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-300 flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-purple-400" />
                Visual Prompt
              </label>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Describe the scene in high detail..."
                className="glass-input w-full min-h-[120px] resize-none"
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-300 flex items-center gap-2">
                <Type className="w-4 h-4 text-pink-400" />
                Text Rendering (Precise)
              </label>
              <input
                type="text"
                value={textInImage}
                onChange={(e) => setTextInImage(e.target.value)}
                placeholder="Exact text to appear in the image..."
                className="glass-input w-full"
              />
            </div>

            <div className="pt-4">
              <button
                onClick={handleGenerate}
                disabled={isGenerating || !prompt}
                className="glass-button-primary w-full py-4 flex items-center justify-center gap-2"
              >
                {isGenerating ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    <span>Synthesizing...</span>
                  </>
                ) : (
                  <>
                    <Image className="w-5 h-5" />
                    <span>Generate Masterpiece</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Quick Features */}
          <div className="grid grid-cols-2 gap-4">
            <div className="glass-card p-4 flex items-center gap-3">
              <div className="p-2 bg-blue-500/20 rounded-lg">
                <Search className="w-5 h-5 text-blue-400" />
              </div>
              <span className="text-xs text-slate-300">Search Grounded</span>
            </div>
            <div className="glass-card p-4 flex items-center gap-3">
              <div className="p-2 bg-green-500/20 rounded-lg">
                <Sparkles className="w-5 h-5 text-green-400" />
              </div>
              <span className="text-xs text-slate-300">4K Upscaling</span>
            </div>
          </div>
        </div>

        {/* Preview Area */}
        <div className="glass-panel min-h-[500px] flex flex-col items-center justify-center p-4 relative group">
          {resultImage ? (
            <motion.div 
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="w-full h-full"
            >
              <img 
                src={resultImage} 
                alt="Generated result" 
                className="w-full h-full object-contain rounded-xl"
              />
              <div className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity">
                <button className="glass-button-secondary !p-2">
                  <Download className="w-5 h-5" />
                </button>
              </div>
            </motion.div>
          ) : (
            <div className="text-center space-y-4 opacity-30">
              <Image className="w-16 h-16 mx-auto" />
              <p>Your creation will appear here</p>
            </div>
          )}
          
          {isGenerating && (
            <div className="absolute inset-0 bg-slate-950/60 backdrop-blur-sm rounded-2xl flex items-center justify-center">
              <div className="text-center">
                <div className="w-12 h-12 border-4 border-purple-500/20 border-t-purple-500 rounded-full animate-spin mx-auto mb-4" />
                <p className="premium-gradient font-medium animate-pulse">Nano Banana 2 is imagining...</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ImageStudio;

