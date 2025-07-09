import React, { useState, useEffect, useRef } from 'react';

const VeoGenVoiceControl = () => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [response, setResponse] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState('');
  const [commandHistory, setCommandHistory] = useState([]);
  
  const recognitionRef = useRef(null);
  const synthesisRef = useRef(window.speechSynthesis);

  // Voice commands for quick testing
  const quickCommands = [
    "Create a cinematic video about Prague sunset",
    "Start a rap battle about artificial intelligence", 
    "What are the benefits of voice control?",
    "Play some relaxing background music",
    "Show me my session status"
  ];

  useEffect(() => {
    // Initialize speech recognition
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = 'en-US';

      recognitionRef.current.onstart = () => {
        setIsListening(true);
        setError('');
      };

      recognitionRef.current.onresult = (event) => {
        const result = event.results[0][0].transcript;
        setTranscript(result);
        processVoiceCommand(result);
      };

      recognitionRef.current.onerror = (event) => {
        setError(`Speech recognition error: ${event.error}`);
        setIsListening(false);
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
      };
    } else {
      setError('Speech recognition not supported in this browser');
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, []);

  const processVoiceCommand = async (command) => {
    setIsProcessing(true);
    setError('');

    try {
      // Process command with Claude AI
      const claudeResponse = await window.claude.complete(`
        Process this voice command for VeoGen video platform: "${command}"
        
        Determine the intent and respond appropriately.
        
        Return JSON format:
        {
          "action": "create_video|answer_question|play_music|rap_battle|status|other",
          "response": "helpful response to speak back to user",
          "parameters": {
            "topic": "extracted topic if relevant",
            "style": "video style if video request",
            "duration": "duration if specified"
          },
          "confidence": 0.8
        }
      `);

      const parsedResponse = JSON.parse(claudeResponse);
      
      // Update response
      setResponse(parsedResponse.response);
      
      // Add to command history
      setCommandHistory(prev => [...prev.slice(-4), {
        command,
        response: parsedResponse.response,
        action: parsedResponse.action,
        timestamp: Date.now()
      }]);

      // Speak the response
      await speakResponse(parsedResponse.response);
      
      // Handle specific actions
      handleAction(parsedResponse);

    } catch (error) {
      console.error('Voice command processing error:', error);
      const errorMessage = "I'm sorry, I had trouble processing that command.";
      setResponse(errorMessage);
      await speakResponse(errorMessage);
    } finally {
      setIsProcessing(false);
    }
  };

  const speakResponse = async (text) => {
    if ('speechSynthesis' in window) {
      return new Promise((resolve) => {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 0.9;
        utterance.pitch = 1.0;
        utterance.volume = 0.8;
        
        utterance.onend = () => resolve();
        utterance.onerror = () => resolve(); // Resolve anyway if speech fails
        
        synthesisRef.current.speak(utterance);
      });
    }
  };

  const handleAction = (parsedResponse) => {
    switch (parsedResponse.action) {
      case 'create_video':
        console.log('🎬 Video creation request:', parsedResponse.parameters);
        // Here you would integrate with VeoGen video creation API
        break;
      
      case 'rap_battle':
        console.log('🎤 Rap battle request:', parsedResponse.parameters);
        // Here you would start the rap battle system
        break;
      
      case 'play_music':
        console.log('🎵 Music request:', parsedResponse.parameters);
        // Here you would integrate with music system
        break;
      
      case 'status':
        console.log('📊 Status request');
        // Show system status
        break;
      
      default:
        console.log('💬 General response');
    }
  };

  const startListening = () => {
    if (recognitionRef.current && !isListening) {
      setTranscript('');
      setResponse('');
      recognitionRef.current.start();
    }
  };

  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
    }
  };

  const useQuickCommand = async (command) => {
    setTranscript(command);
    await processVoiceCommand(command);
  };

  const clearHistory = () => {
    setCommandHistory([]);
    setTranscript('');
    setResponse('');
    setError('');
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 text-white rounded-lg shadow-2xl">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold mb-2">🎤 VeoGen Voice Control</h1>
        <p className="text-blue-300">AI-powered voice interface for video generation</p>
      </div>

      {/* Voice Control Section */}
      <div className="bg-black/20 rounded-lg p-6 mb-6">
        <div className="flex flex-col items-center space-y-4">
          {/* Main Voice Button */}
          <button
            onClick={isListening ? stopListening : startListening}
            disabled={isProcessing}
            className={`
              w-32 h-32 rounded-full text-4xl font-bold transition-all duration-300 shadow-lg
              ${isListening 
                ? 'bg-red-500 hover:bg-red-600 animate-pulse' 
                : 'bg-blue-500 hover:bg-blue-600'
              }
              ${isProcessing ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
            `}
          >
            {isProcessing ? '⏳' : isListening ? '🔴' : '🎤'}
          </button>

          {/* Status Text */}
          <div className="text-center">
            {isProcessing && (
              <p className="text-yellow-300 animate-pulse">Processing command...</p>
            )}
            {isListening && !isProcessing && (
              <p className="text-green-300">Listening... Speak now!</p>
            )}
            {!isListening && !isProcessing && (
              <p className="text-blue-300">Click to start voice command</p>
            )}
          </div>

          {/* Error Display */}
          {error && (
            <div className="bg-red-500/20 border border-red-500 rounded-lg p-3 text-red-300">
              ⚠️ {error}
            </div>
          )}
        </div>
      </div>

      {/* Current Interaction */}
      {(transcript || response) && (
        <div className="bg-black/20 rounded-lg p-6 mb-6">
          <h3 className="text-xl font-semibold mb-4">🗣️ Current Interaction</h3>
          
          {transcript && (
            <div className="mb-4">
              <p className="text-blue-300 font-medium">You said:</p>
              <p className="bg-blue-500/20 rounded p-3 mt-2">"{transcript}"</p>
            </div>
          )}
          
          {response && (
            <div>
              <p className="text-green-300 font-medium">VeoGen Assistant:</p>
              <p className="bg-green-500/20 rounded p-3 mt-2">{response}</p>
            </div>
          )}
        </div>
      )}

      {/* Quick Commands */}
      <div className="bg-black/20 rounded-lg p-6 mb-6">
        <h3 className="text-xl font-semibold mb-4">⚡ Quick Commands</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {quickCommands.map((command, index) => (
            <button
              key={index}
              onClick={() => useQuickCommand(command)}
              disabled={isListening || isProcessing}
              className="bg-indigo-500/30 hover:bg-indigo-500/50 disabled:opacity-50 disabled:cursor-not-allowed border border-indigo-400 rounded-lg p-3 text-left transition-all text-sm"
            >
              "{command}"
            </button>
          ))}
        </div>
      </div>

      {/* Command History */}
      {commandHistory.length > 0 && (
        <div className="bg-black/20 rounded-lg p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-xl font-semibold">📋 Recent Commands</h3>
            <button
              onClick={clearHistory}
              className="bg-red-500/30 hover:bg-red-500/50 text-red-300 px-3 py-1 rounded text-sm transition-all"
            >
              Clear History
            </button>
          </div>
          
          <div className="space-y-3 max-h-60 overflow-y-auto">
            {commandHistory.slice().reverse().map((item, index) => (
              <div key={index} className="bg-gray-800/50 rounded p-3">
                <div className="flex justify-between items-start mb-2">
                  <span className="text-blue-300 text-sm">
                    {new Date(item.timestamp).toLocaleTimeString()}
                  </span>
                  <span className="bg-indigo-500/30 text-indigo-200 px-2 py-1 rounded text-xs">
                    {item.action}
                  </span>
                </div>
                <p className="text-gray-300 text-sm mb-1">
                  <strong>Command:</strong> "{item.command}"
                </p>
                <p className="text-gray-400 text-sm">
                  <strong>Response:</strong> {item.response}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Footer Info */}
      <div className="mt-8 text-center text-gray-400 text-sm">
        <p>💡 Powered by window.claude.complete | 🎬 Integrated with VeoGen AI Video Platform</p>
        <p className="mt-1">Try saying: "Create a video about..." or "Start a rap battle about..."</p>
      </div>
    </div>
  );
};

export default VeoGenVoiceControl;