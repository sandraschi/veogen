/**
 * 🎭 Creative AI Applications
 * Music, stories, rap battles, and artistic content generation
 */

import ClaudeQuery from './claude-query.js';

const CreativeAI = {
  
  // Generate song lyrics
  async generateSongLyrics(genre, theme, mood) {
    const prompt = `Write song lyrics in ${genre} style about ${theme}.
Mood: ${mood}

Include:
- Verse 1
- Chorus  
- Verse 2
- Chorus
- Bridge
- Final Chorus

Make it emotionally resonant and fitting for the genre.`;
    
    return await ClaudeQuery.queryWithRetry(prompt);
  },

  // Create rap battle
  async createRapBattle(participants, topic, rounds = 2) {
    const battle = [];
    
    for (let round = 1; round <= rounds; round++) {
      for (const participant of participants) {
        const previousVerses = battle.slice(-2).map(b => b.verse).join('\n');
        
        const prompt = `Generate a rap verse for ${participant.name} in round ${round} about ${topic}.
${previousVerses ? `Respond to: "${previousVerses}"` : ''}

Style: ${participant.style || 'clever'}
Make it ${round === rounds ? 'explosive' : 'building'} with clever wordplay.
4-6 lines maximum.`;

        const verse = await ClaudeQuery.queryWithRetry(prompt);
        
        battle.push({
          participant: participant.name,
          round: round,
          verse: verse.trim(),
          timestamp: Date.now()
        });
        
        // Brief pause between verses
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }
    
    return battle;
  },

  // Generate interactive story
  async generateStoryFromVoice(transcript, genre = 'adventure') {
    const prompt = `Create an interactive story outline from: "${transcript}"

Genre: ${genre}

Return JSON:
{
  "title": "story title",
  "setting": "when and where", 
  "characters": [{"name": "", "role": "", "description": ""}],
  "opening_scene": "detailed opening",
  "first_choices": ["choice 1", "choice 2", "choice 3"],
  "themes": ["theme1", "theme2"]
}`;
    
    return await ClaudeQuery.queryWithRetry(prompt, { parseJSON: true });
  },

  // Continue story
  async continueStory(currentState, userChoice) {
    const prompt = `Continue this interactive story:
Current state: ${JSON.stringify(currentState)}
User chose: "${userChoice}"

Write the next scene (2-3 paragraphs) and provide 3 new choices.
Maintain consistency with established characters and plot.

Return JSON:
{
  "scene_description": "what happens next",
  "character_dialogue": "any character speech", 
  "choices": ["choice 1", "choice 2", "choice 3"],
  "updated_state": {...updated game state...}
}`;
    
    return await ClaudeQuery.queryWithRetry(prompt, { parseJSON: true });
  },

  // Generate video script
  async generateVideoScript(topic, style, duration) {
    const prompt = `Create a detailed video script for a ${duration}-second ${style} video about ${topic}.

Include:
- Scene descriptions
- Voiceover text  
- Visual cues
- Timing markers
- Suggested music/sound

Format as a professional script with clear sections.`;
    
    return await ClaudeQuery.queryWithRetry(prompt);
  },

  // Describe visual concept
  async describeVisualConcept(concept, medium = 'video') {
    const prompt = `Create a detailed visual concept description for ${medium}:
Concept: "${concept}"

Include:
- Visual style and aesthetics
- Color palette
- Composition and framing
- Mood and atmosphere  
- Technical considerations
- Reference inspirations

Make it detailed enough for artists/creators to execute.`;
    
    return await ClaudeQuery.queryWithRetry(prompt);
  }
};

export default CreativeAI;