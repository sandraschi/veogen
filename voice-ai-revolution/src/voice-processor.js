/**
 * 🎤 Voice Command Processor
 * Core voice input processing and pattern recognition
 */

const VoiceCommandProcessor = {
  patterns: {
    videoGeneration: /(?:create|make|generate|build)\s+(?:a\s+)?(?:video|clip|movie)\s+(?:about|of|featuring)\s+(.+)/i,
    musicRequest: /(?:play|start|put on)\s+(?:some\s+)?(.+?)(?:\s+music)?$/i,
    questionPattern: /(?:what|how|why|when|where|who)\s+(.+)/i,
    commandPattern: /(?:can you|please|could you)\s+(.+)/i,
    rapBattle: /(?:rap battle|battle rap|start.*battle)\s*(?:about\s+(.+))?/i,
    statusCheck: /(?:status|how.*doing|what.*up)/i
  },

  async processCommand(transcript) {
    const cleanTranscript = transcript.trim().toLowerCase();
    
    // Try pattern matching first
    for (const [type, pattern] of Object.entries(this.patterns)) {
      const match = cleanTranscript.match(pattern);
      if (match) {
        return await this.handleSpecificCommand(type, match[1] || '', transcript);
      }
    }
    
    // Fallback to general AI processing
    return await this.handleGeneralCommand(transcript);
  },

  async handleSpecificCommand(type, extracted, original) {
    const prompts = {
      videoGeneration: `Extract video parameters from: "${original}"
Return JSON only: {"action": "create_video", "topic": "${extracted}", "duration": 30, "style": "cinematic", "mood": "upbeat"}`,
      
      musicRequest: `Process music request: "${original}"
Return JSON only: {"action": "play_music", "genre": "${extracted}", "mood": "upbeat", "tempo": "medium"}`,
      
      questionPattern: `Answer briefly: "${original}"`,
      
      rapBattle: `Generate a 4-line rap verse about ${extracted || 'AI'}. Make it clever and rhyme well.`,
      
      statusCheck: `Return JSON only: {"action": "status", "response": "Voice assistant is active and ready!"}`
    };

    try {
      const response = await window.claude.complete(prompts[type]);
      
      if (type === 'questionPattern' || type === 'rapBattle') {
        return {
          type: 'answer',
          response: response.trim(),
          action: 'speak'
        };
      }
      
      return JSON.parse(response);
    } catch (error) {
      console.error(`Error processing ${type}:`, error);
      return {
        type: 'error',
        response: "I didn't understand that completely. Could you try again?",
        action: 'speak'
      };
    }
  },

  async handleGeneralCommand(transcript) {
    const prompt = `Process voice command: "${transcript}"
Return JSON only: {"type": "video|music|question|conversation", "response": "helpful response", "action": "speak|create_video|play_music", "confidence": 0.8}`;

    try {
      const response = await window.claude.complete(prompt);
      return JSON.parse(response);
    } catch (error) {
      return {
        type: 'unknown',
        response: "Could you rephrase that?",
        action: 'speak',
        confidence: 0.1
      };
    }
  }
};

export default VoiceCommandProcessor;