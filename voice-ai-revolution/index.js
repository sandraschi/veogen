/**
 * 🎤 VeoGen Voice AI Revolution - Main Export
 * Clean, modular voice control system
 */

import VoiceCommandProcessor from './src/voice-processor.js';
import ClaudeQuery from './src/claude-query.js';
import VoiceInterface from './src/voice-interface.js';
import ContextManager from './src/context-manager.js';
import VoiceAssistant from './src/voice-assistant.js';
import CreativeAI from './src/creative-ai.js';

// Quick setup functions
const createBasicVoiceAssistant = async (userId = 'user', userData = {}) => {
  const assistant = new VoiceAssistant({
    language: 'en-US',
    voiceGender: 'male',
    responseStyle: 'conversational'
  });
  
  await assistant.initialize(userId, userData);
  return assistant;
};

const createVideoProductionAssistant = async (userId = 'producer') => {
  const assistant = new VoiceAssistant({
    responseStyle: 'professional'
  });
  
  await assistant.initialize(userId, {
    name: 'Video Producer',
    videoPreferences: {
      defaultStyle: 'cinematic',
      defaultDuration: 60,
      quality: 'HD'
    }
  });
  
  return assistant;
};

// Browser exports
if (typeof window !== 'undefined') {
  window.VeoGenVoice = {
    VoiceCommandProcessor,
    ClaudeQuery,
    VoiceInterface,
    ContextManager,
    VoiceAssistant,
    CreativeAI,
    createBasicVoiceAssistant,
    createVideoProductionAssistant
  };
}

// Module exports
export {
  VoiceCommandProcessor,
  ClaudeQuery,
  VoiceInterface,
  ContextManager,
  VoiceAssistant,
  CreativeAI,
  createBasicVoiceAssistant,
  createVideoProductionAssistant
};

// Auto-initialization message
document?.addEventListener('DOMContentLoaded', () => {
  console.log('🎤 VeoGen Voice AI Revolution loaded!');
  console.log('Available at window.VeoGenVoice');
  console.log('Quick start: const assistant = await createBasicVoiceAssistant()');
});

/**
 * 🎊 Clean, Modular Voice Control System
 * 
 * ✅ 6 focused modules (~100-150 lines each)
 * ✅ Clear separation of concerns
 * ✅ Easy to understand and maintain
 * ✅ Production-ready patterns
 * ✅ Full window.claude.complete integration
 * 
 * Much better than one 1000+ line monster file! 🚀
 */