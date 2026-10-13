/**
 * 🎙️ Voice Interface Manager
 * Speech recognition and text-to-speech functionality
 */

const VoiceInterface = {
  recognition: null,
  synthesis: window.speechSynthesis,
  isListening: false,
  currentVoice: null,

  // Initialize speech recognition
  initRecognition(options = {}) {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      throw new Error('Speech recognition not supported');
    }
    
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    this.recognition = new SpeechRecognition();
    
    this.recognition.continuous = options.continuous || false;
    this.recognition.interimResults = options.interimResults || true;
    this.recognition.lang = options.language || 'en-US';
    
    return this.recognition;
  },

  // Start listening
  async startListening(onResult, onError = null) {
    if (!this.recognition) {
      this.initRecognition();
    }
    
    return new Promise((resolve, reject) => {
      this.recognition.onstart = () => {
        this.isListening = true;
        console.log('🎤 Listening started');
        resolve(true);
      };
      
      this.recognition.onresult = async (event) => {
        const results = Array.from(event.results);
        const latest = results[results.length - 1];
        
        if (latest.isFinal) {
          const transcript = latest[0].transcript.trim();
          console.log('Voice input:', transcript);
          
          try {
            await onResult(transcript);
          } catch (error) {
            console.error('Error processing voice:', error);
            if (onError) onError(error);
          }
        }
      };
      
      this.recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        this.isListening = false;
        if (onError) onError(new Error(event.error));
        else reject(new Error(event.error));
      };
      
      this.recognition.onend = () => {
        this.isListening = false;
        console.log('🎤 Listening ended');
      };
      
      this.recognition.start();
    });
  },

  // Stop listening
  stopListening() {
    if (this.recognition && this.isListening) {
      this.recognition.stop();
    }
  },

  // Initialize voices
  async initVoices() {
    return new Promise((resolve) => {
      const loadVoices = () => {
        const voices = this.synthesis.getVoices();
        this.currentVoice = voices.find(voice => 
          voice.lang.startsWith('en') && voice.name.includes('David')
        ) || voices.find(voice => voice.lang.startsWith('en')) || voices[0];
        
        resolve(voices);
      };
      
      if (this.synthesis.getVoices().length > 0) {
        loadVoices();
      } else {
        this.synthesis.onvoiceschanged = loadVoices;
      }
    });
  },

  // Speak text
  async speak(text, options = {}) {
    if (!this.currentVoice) {
      await this.initVoices();
    }
    
    return new Promise((resolve, reject) => {
      this.synthesis.cancel();
      
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.voice = options.voice || this.currentVoice;
      utterance.rate = options.rate || 0.9;
      utterance.pitch = options.pitch || 1.0;
      utterance.volume = options.volume || 0.8;
      
      // Apply emotion
      if (options.emotion) {
        this.applyEmotion(utterance, options.emotion);
      }
      
      utterance.onend = () => resolve(true);
      utterance.onerror = (event) => reject(new Error(event.error));
      
      this.synthesis.speak(utterance);
    });
  },

  // Apply emotional modulation
  applyEmotion(utterance, emotion) {
    const emotions = {
      excited: { rate: 1.2, pitch: 1.3 },
      calm: { rate: 0.8, pitch: 0.9 },
      confident: { rate: 1.0, pitch: 1.1 },
      thoughtful: { rate: 0.7, pitch: 0.95 }
    };
    
    const settings = emotions[emotion] || emotions.confident;
    Object.assign(utterance, settings);
  },

  // Stop speaking
  stopSpeaking() {
    this.synthesis.cancel();
  }
};

export default VoiceInterface;