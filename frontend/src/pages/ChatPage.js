import {
  ChatBubbleLeftRightIcon,
  PaperAirplaneIcon,
  SparklesIcon,
  SpeakerWaveIcon,
  StopIcon,
} from '@heroicons/react/24/outline';
import { AnimatePresence, motion } from 'framer-motion';
import React, { useState, useRef, useEffect } from 'react';
import { toast } from 'sonner';

const ChatPage = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const messagesEndRef = useRef(null);
  const audioRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // biome-ignore lint/correctness/useExhaustiveDependencies: messages is the intended trigger; scrollToBottom only touches a ref
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isTyping) return;

    const userMsg = {
      id: Date.now(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputMessage('');
    setIsTyping(true);

    try {
      // Modern 2026 Fleet API endpoint
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: inputMessage }),
      });

      const data = await response.json();

      const aiMsg = {
        id: Date.now() + 1,
        type: 'assistant',
        content: data.message,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, aiMsg]);

      // Auto-trigger TTS if enabled
      if (data.audio_url) {
        handlePlayTTS(data.audio_url);
      }
    } catch (_error) {
      toast.error('Failed to get response from Gemini 3.1');
    } finally {
      setIsTyping(false);
    }
  };

  const handlePlayTTS = async (audioUrl) => {
    setIsSpeaking(true);
    try {
      if (audioRef.current) {
        audioRef.current.src = audioUrl;
        await audioRef.current.play();
      }
    } catch (_error) {
      toast.error('Flash TTS playback failed');
    } finally {
      setIsSpeaking(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-120px)] max-w-5xl mx-auto">
      <audio ref={audioRef} onEnded={() => setIsSpeaking(false)} hidden>
        <track kind="captions" />
      </audio>

      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold premium-gradient">Gemini 3.1 Workspace</h1>
          <p className="text-slate-400">Powered by Gemini 3.1 Pro & Flash TTS</p>
        </div>
        <div className="flex items-center space-x-2">
          {isSpeaking && (
            <div className="flex items-center space-x-2 px-3 py-1 bg-purple-500/20 rounded-full border border-purple-500/30">
              <div className="animate-pulse bg-purple-400 w-2 h-2 rounded-full" />
              <span className="text-xs font-medium text-purple-300">Speaking...</span>
            </div>
          )}
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 glass-panel overflow-hidden flex flex-col mb-4">
        <div className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-hide">
          <AnimatePresence>
            {messages.length === 0 && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="h-full flex flex-col items-center justify-center text-center opacity-40"
              >
                <SparklesIcon className="w-16 h-16 mb-4 text-purple-400" />
                <p className="text-xl">How can I assist your creative process today?</p>
              </motion.div>
            )}
            {messages.map((m) => (
              <motion.div
                key={m.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex ${m.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] p-4 rounded-2xl ${
                    m.type === 'user'
                      ? 'bg-gradient-to-r from-purple-600 to-indigo-600 shadow-lg shadow-purple-900/20'
                      : 'bg-white/5 border border-white/10'
                  }`}
                >
                  <p className="text-sm leading-relaxed">{m.content}</p>
                  <div className="flex items-center justify-between mt-2 opacity-50 text-[10px]">
                    <span>{m.timestamp.toLocaleTimeString()}</span>
                    {m.type === 'assistant' && (
                      <button type="button" className="hover:text-purple-400 transition-colors">
                        <SpeakerWaveIcon className="w-3 h-3" />
                      </button>
                    )}
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
          {isTyping && (
            <div className="flex space-x-2 p-4 bg-white/5 rounded-2xl w-20">
              <div className="w-1.5 h-1.5 bg-purple-400 rounded-full animate-bounce" />
              <div className="w-1.5 h-1.5 bg-purple-400 rounded-full animate-bounce [animation-delay:0.2s]" />
              <div className="w-1.5 h-1.5 bg-purple-400 rounded-full animate-bounce [animation-delay:0.4s]" />
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input area */}
        <div className="p-4 border-t border-white/5 bg-black/20">
          <div className="flex items-center space-x-3">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
              placeholder="Message Gemini 3.1..."
              className="flex-1 glass-input"
            />
            <button
              type="button"
              onClick={handleSendMessage}
              disabled={!inputMessage.trim() || isTyping}
              className="glass-button-primary !p-3 rounded-xl"
            >
              <PaperAirplaneIcon className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;
