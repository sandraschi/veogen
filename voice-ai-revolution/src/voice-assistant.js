/**
 * 🎤 Voice Assistant - Main Controller
 * Orchestrates all voice interaction components
 */

import VoiceCommandProcessor from './voice-processor.js';
import ClaudeQuery from './claude-query.js';
import VoiceInterface from './voice-interface.js';
import ContextManager from './context-manager.js';

class VoiceAssistant {
  constructor(options = {}) {
    this.contextManager = new ContextManager();
    this.isInitialized = false;
    this.isListening = false;
    this.currentUser = null;
    this.settings = {
      language: 'en-US',
      voiceGender: 'male',
      responseStyle: 'conversational',
      autoListen: false,
      ...options
    };
    
    this.eventListeners = {
      onTranscript: [],
      onResponse: [],
      onError: [],
      onStateChange: []
    };
  }

  // Initialize the assistant
  async initialize(userId = 'default', userData = {}) {
    try {
      await VoiceInterface.initVoices();
      VoiceInterface.initRecognition({
        continuous: this.settings.autoListen,
        language: this.settings.language
      });
      
      this.currentUser = userId;
      this.contextManager.createContext(userId, {
        name: userData.name || 'User',
        preferences: {
          voiceStyle: this.settings.responseStyle,
          topics: userData.interests || [],
          videoPreferences: userData.videoPreferences || {}
        },
        session: {
          startTime: Date.now(),
          interactions: 0
        }
      });
      
      this.isInitialized = true;
      this.notifyStateChange('initialized');
      
      return true;
    } catch (error) {
      console.error('Failed to initialize voice assistant:', error);
      this.notifyError(error);
      throw error;
    }
  }

  // Start listening
  async startListening() {
    if (!this.isInitialized) {
      throw new Error('Voice assistant not initialized');
    }
    
    this.isListening = true;
    this.notifyStateChange('listening');
    
    try {
      await VoiceInterface.startListening(
        (transcript) => this.processVoiceInput(transcript),
        (error) => this.handleVoiceError(error)
      );
    } catch (error) {
      this.isListening = false;
      this.notifyStateChange('error');
      throw error;
    }
  }

  // Stop listening
  stopListening() {
    VoiceInterface.stopListening();
    this.isListening = false;
    this.notifyStateChange('idle');
  }

  // Process voice input
  async processVoiceInput(transcript) {
    try {
      this.notifyTranscript(transcript);
      this.notifyStateChange('processing');
      
      // Update interaction count
      const context = this.contextManager.getContext(this.currentUser);
      context.data.session.interactions++;
      
      // Process with context
      const response = await this.contextManager.queryWithContext(
        this.currentUser,
        this.buildVoicePrompt(transcript),
        { 
          lastCommand: transcript,
          commandTime: Date.now()
        }
      );
      
      const parsedResponse = await this.parseResponse(response);
      
      this.notifyResponse(parsedResponse);
      this.notifyStateChange('responding');
      
      // Speak response
      await VoiceInterface.speak(parsedResponse.response, {
        emotion: this.getEmotionForResponse(parsedResponse)
      });
      
      this.notifyStateChange(this.settings.autoListen ? 'listening' : 'idle');
      
      return parsedResponse;
    } catch (error) {
      console.error('Error processing voice input:', error);
      this.handleVoiceError(error);
      throw error;
    }
  }

  // Build voice prompt with context
  buildVoicePrompt(transcript) {
    const context = this.contextManager.getContext(this.currentUser);
    
    return `
Process voice command: "${transcript}"

User: ${context.data.name}
Preferences: ${JSON.stringify(context.data.preferences)}
Session interactions: ${context.data.session.interactions}

Return JSON format:
{
  "action": "create_video|respond|clarify|command",
  "response": "text to speak",
  "data": {...parameters...},
  "confidence": 0.0-1.0
}
    `.trim();
  }

  // Parse AI response
  async parseResponse(response) {
    try {
      const parsed = JSON.parse(response);
      
      switch (parsed.action) {
        case 'create_video':
          return await this.handleVideoCreation(parsed);
        default:
          return parsed;
      }
    } catch (error) {
      return {
        action: 'respond',
        response: "I had trouble understanding that. Could you try again?",
        confidence: 0.1
      };
    }
  }

  // Handle video creation
  async handleVideoCreation(parsedResponse) {
    const videoData = parsedResponse.data || {};
    console.log('Video creation request:', videoData);
    
    return {
      ...parsedResponse,
      response: `Creating a ${videoData.style || 'cinematic'} video about ${videoData.topic || 'your request'}.`
    };
  }

  // Get emotion for response
  getEmotionForResponse(response) {
    if (response.action === 'create_video') return 'excited';
    if (response.confidence < 0.3) return 'thoughtful';
    return 'confident';
  }

  // Handle errors
  handleVoiceError(error) {
    console.error('Voice error:', error);
    this.notifyError(error);
    VoiceInterface.speak("I'm having trouble with voice recognition. Please try again.");
  }

  // Event system
  addEventListener(eventType, callback) {
    if (this.eventListeners[eventType]) {
      this.eventListeners[eventType].push(callback);
    }
  }

  notifyTranscript(transcript) {
    this.eventListeners.onTranscript.forEach(cb => cb(transcript));
  }

  notifyResponse(response) {
    this.eventListeners.onResponse.forEach(cb => cb(response));
  }

  notifyError(error) {
    this.eventListeners.onError.forEach(cb => cb(error));
  }

  notifyStateChange(state) {
    this.eventListeners.onStateChange.forEach(cb => cb(state));
  }

  // Get status
  getStatus() {
    return {
      initialized: this.isInitialized,
      listening: this.isListening,
      currentUser: this.currentUser,
      settings: this.settings
    };
  }

  // Shutdown
  shutdown() {
    this.stopListening();
    VoiceInterface.stopSpeaking();
    this.isInitialized = false;
    this.notifyStateChange('shutdown');
  }
}

export default VoiceAssistant;