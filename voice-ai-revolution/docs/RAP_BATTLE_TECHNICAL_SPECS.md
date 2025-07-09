) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}
```

## 🎯 Sample Battle Implementation

### **Complete Rap Battle Component**
```javascript
const RapBattleArena = () => {
  const [battle, setBattle] = useState(null);
  const [currentRound, setCurrentRound] = useState(0);
  const [battleState, setBattleState] = useState('ready'); // ready, battling, complete
  const [scores, setScores] = useState({ claude: 0, gemini: 0, ties: 0 });
  const [deliverySystem] = useState(() => new RapDeliverySystem());

  const topics = [
    'artificial intelligence',
    'video generation',
    'machine learning',
    'the future of technology',
    'digital creativity',
    'code and algorithms',
    'data processing',
    'neural networks'
  ];

  const startBattle = async (topic, rounds = 2) => {
    setBattleState('battling');
    setCurrentRound(0);
    
    const newBattle = {
      topic,
      rounds,
      verses: { claude: [], gemini: [] },
      scores: [],
      timestamp: Date.now()
    };
    
    setBattle(newBattle);

    try {
      // Epic battle introduction
      await deliverySystem.speak(
        `🎤 WELCOME TO THE AI RAP BATTLE ARENA! 🎤`, 
        { rate: 1.3, pitch: 1.3, volume: 1.0 }
      );
      
      await deliverySystem.pause(1000);
      
      await deliverySystem.speak(
        `Tonight's topic: ${topic.toUpperCase()}! Let's see who drops the sickest bars!`,
        { rate: 1.1, pitch: 1.2 }
      );

      // Execute battle rounds
      for (let round = 1; round <= rounds; round++) {
        setCurrentRound(round);
        await executeRound(newBattle, round);
      }

      // Battle conclusion
      await deliverySystem.speak(
        'What an EPIC battle! The crowd goes absolutely wild!',
        { rate: 1.2, pitch: 1.3 }
      );

      setBattleState('complete');
      
    } catch (error) {
      console.error('Battle error:', error);
      await deliverySystem.speak('Technical difficulties in the arena! Please try again.');
      setBattleState('ready');
    }
  };

  const executeRound = async (battleData, roundNum) => {
    await deliverySystem.announceRound(roundNum, battleData.topic);

    // Claude's verse
    const claudePrompt = `
    You're Claude in an AI rap battle! Round ${roundNum} about ${battleData.topic}.
    
    ${roundNum > 1 ? `Previous battle context: ${battleData.verses.gemini.slice(-1)[0] || ''}` : ''}
    
    Your style: Technical wordplay, AI terminology, confident but analytical
    Write 4-6 lines with solid rhymes. Be clever and sharp!
    `;

    const claudeVerse = await window.claude.complete(claudePrompt);
    battleData.verses.claude.push(claudeVerse);

    await deliverySystem.deliverRapVerse('Claude', claudeVerse, { emphasize: true });

    // Dramatic pause between verses
    await deliverySystem.pause(1500);

    // Gemini's response
    const geminiPrompt = `
    You're Google Gemini responding to Claude in round ${roundNum} about ${battleData.topic}.
    
    Claude just said: "${claudeVerse}"
    
    Your style: Creative, visual, multimodal references, bold and flashy
    Fire back with 4-6 lines! Make it catchy and confident!
    `;

    const geminiVerse = await window.claude.complete(geminiPrompt);
    battleData.verses.gemini.push(geminiVerse);

    await deliverySystem.deliverRapVerse('Gemini', geminiVerse, { emphasize: true });

    setBattle({...battleData});
  };

  const voteForWinner = (winner) => {
    const newScores = { ...scores };
    newScores[winner]++;
    setScores(newScores);
    
    deliverySystem.speak(`Point goes to ${winner}! The crowd cheers!`);
  };

  return (
    <div className="rap-battle-arena">
      <div className="arena-header">
        <h1>🎤 AI RAP BATTLE ARENA 🎤</h1>
        <div className="scoreboard">
          <div>Claude: {scores.claude}</div>
          <div>Gemini: {scores.gemini}</div>
          <div>Ties: {scores.ties}</div>
        </div>
      </div>

      {battleState === 'ready' && (
        <div className="battle-setup">
          <h2>Choose Your Battle Topic:</h2>
          <div className="topic-buttons">
            {topics.map(topic => (
              <button
                key={topic}
                onClick={() => startBattle(topic, 2)}
                className="topic-button"
              >
                🎯 {topic}
              </button>
            ))}
          </div>
          
          <div className="custom-topic">
            <input 
              type="text" 
              placeholder="Or enter custom topic..."
              onKeyPress={(e) => {
                if (e.key === 'Enter' && e.target.value.trim()) {
                  startBattle(e.target.value.trim(), 2);
                }
              }}
            />
          </div>
        </div>
      )}

      {battleState === 'battling' && battle && (
        <div className="battle-in-progress">
          <h2>🔥 BATTLE IN PROGRESS 🔥</h2>
          <div className="battle-info">
            <div>Topic: <strong>{battle.topic}</strong></div>
            <div>Round: <strong>{currentRound} / {battle.rounds}</strong></div>
          </div>
          
          <div className="battle-status">
            <div className="status-indicator">
              🎤 AIs are dropping bars...
            </div>
          </div>
        </div>
      )}

      {battleState === 'complete' && battle && (
        <div className="battle-results">
          <h2>🏆 BATTLE COMPLETE! 🏆</h2>
          
          <div className="verses-display">
            {battle.verses.claude.map((verse, index) => (
              <div key={index} className="round-display">
                <h3>Round {index + 1}</h3>
                
                <div className="verse claude-verse">
                  <h4>🧠 Claude:</h4>
                  <p className="verse-text">"{verse}"</p>
                </div>
                
                <div className="verse gemini-verse">
                  <h4>⚡ Gemini:</h4>
                  <p className="verse-text">"{battle.verses.gemini[index]}"</p>
                </div>
                
                <div className="round-voting">
                  <h4>Who won this round?</h4>
                  <button onClick={() => voteForWinner('claude')}>
                    Vote Claude 🧠
                  </button>
                  <button onClick={() => voteForWinner('gemini')}>
                    Vote Gemini ⚡
                  </button>
                  <button onClick={() => voteForWinner('ties')}>
                    It's a Tie! 🤝
                  </button>
                </div>
              </div>
            ))}
          </div>

          <div className="battle-actions">
            <button 
              onClick={() => setBattleState('ready')}
              className="new-battle-button"
            >
              🔄 Start New Battle
            </button>
            
            <button 
              onClick={() => {
                // Replay the battle with TTS
                battle.verses.claude.forEach((verse, i) => {
                  setTimeout(() => {
                    deliverySystem.deliverRapVerse('Claude', verse);
                  }, i * 4000);
                  
                  setTimeout(() => {
                    deliverySystem.deliverRapVerse('Gemini', battle.verses.gemini[i]);
                  }, i * 4000 + 2000);
                });
              }}
              className="replay-button"
            >
              🔊 Replay Battle
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
```

## 🎭 The Comedy Reality

### **Why It's Hilariously Awesome**

#### **The Lyrics**: Surprisingly Good ✅
- **Proper rhyme schemes**: Claude understands ABAB, AABB patterns
- **Technical wordplay**: "Neural networks fire", "parameters align"
- **Clever references**: AI terminology used naturally
- **Flow structure**: Internal rhymes and good rhythm on paper

#### **The Delivery**: Robot Professor Mode ❌😂
- **Windows TTS**: Sounds like Microsoft David reading technical documentation
- **Zero rhythm**: No understanding of musical timing or beats
- **Overly polite**: "My algorithms are quite efficient, if I may say so"
- **No street cred**: Like your computer science professor trying to be cool

### **Sample Real Claude Rap**
```
My neural networks fire with precision so clean,
Processing context like you've never seen,
While Gemini's flashy with multimodal flair,
I analyze deeply with reasoning to spare!
```

**Delivered by TTS**: Imagine David Attenborough narrating a nature documentary about hip-hop culture. Absolutely hilarious! 🤖🎤

### **The Unintentional Comedy Gold**
- **Pause timing**: Perfect lyrical pauses ruined by robotic delivery
- **Emphasis**: "My ALGORITHMS are TIGHT" with zero swagger
- **Pronunciation**: "Neural networks" pronounced like a medical textbook
- **Confidence**: Technically confident lyrics, delivered with the energy of reading terms of service

## 🔧 Technical Implementation Notes

### **Performance Optimization**
```javascript
// Batch TTS requests to avoid browser limitations
const ttsQueue = [];
let isProcessingQueue = false;

const queueTTS = (text, options) => {
  return new Promise((resolve) => {
    ttsQueue.push({ text, options, resolve });
    processQueue();
  });
};

const processQueue = async () => {
  if (isProcessingQueue || ttsQueue.length === 0) return;
  
  isProcessingQueue = true;
  
  while (ttsQueue.length > 0) {
    const { text, options, resolve } = ttsQueue.shift();
    
    const utterance = new SpeechSynthesisUtterance(text);
    Object.assign(utterance, options);
    
    await new Promise((utteranceResolve) => {
      utterance.onend = utteranceResolve;
      speechSynthesis.speak(utterance);
    });
    
    resolve();
  }
  
  isProcessingQueue = false;
};
```

### **Error Handling**
```javascript
const robustRapGeneration = async (prompt, retries = 3) => {
  for (let i = 0; i < retries; i++) {
    try {
      const verse = await window.claude.complete(prompt);
      
      // Validate the verse has reasonable length and structure
      if (verse.length > 20 && verse.includes('\n')) {
        return verse;
      }
      
      throw new Error('Invalid verse structure');
    } catch (error) {
      if (i === retries - 1) {
        // Fallback to a pre-written verse
        return getFallbackVerse();
      }
      
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  }
};

const getFallbackVerse = () => {
  const fallbacks = [
    "Technical difficulties in the house tonight,\nBut my backup bars are still airtight!",
    "Even when my systems glitch and fail,\nMy rap game's strong, my flow's still hail!"
  ];
  
  return fallbacks[Math.floor(Math.random() * fallbacks.length)];
};
```

## 🎤 Conclusion

The AI Rap Battle feature perfectly demonstrates the creative possibilities of `window.claude.complete`. While Claude can write surprisingly good rap lyrics with proper rhyme schemes and clever wordplay, the delivery via text-to-speech creates unintentional comedy gold.

The technical implementation showcases real-time AI creativity, voice synthesis, and interactive entertainment - all built with a simple function call. It's both a proof of concept for AI capabilities and a source of endless entertainment.

**The bottom line**: Claude can drop bars, but they sound like they're being delivered at a poetry reading in a library. And that's exactly what makes it perfect! 🤖🎤

---

*Status: Rap battles documented and preserved for posterity! The robot revolution has never sounded so polite! 🎭🔥*      specialties: ['creativity', 'visual_metaphors', 'storytelling', 'innovation']
    });
  }

  static createCustom(config) {
    return new BattleParticipant(config);
  }

  getPersonalityPromptModifier() {
    const modifiers = {
      analytical_clever: 'Focus on logical wordplay, clever observations, and intellectual bars. Use technical metaphors and precise language.',
      
      creative_visual: 'Emphasize vivid imagery, artistic metaphors, and creative storytelling. Paint pictures with words.',
      
      aggressive_competitive: 'Deliver hard-hitting, competitive bars with confidence and intensity. Go for the knockout.',
      
      smooth_storyteller: 'Weave narratives into verses, use smooth flow and compelling character development.',
      
      technical_wordsmith: 'Focus on complex rhyme schemes, internal rhymes, and technical rap skills.'
    };
    
    return modifiers[this.personality] || modifiers.analytical_clever;
  }

  updateStats(battleResult) {
    this.stats.battles++;
    if (battleResult.won) {
      this.stats.wins++;
    }
    this.stats.totalScore += battleResult.averageScore;
    
    if (!this.stats.bestVerse || battleResult.bestScore > this.stats.bestVerse.score) {
      this.stats.bestVerse = {
        verse: battleResult.bestVerse,
        score: battleResult.bestScore,
        battle: battleResult.battleId
      };
    }
  }

  getWinRate() {
    return this.stats.battles > 0 ? (this.stats.wins / this.stats.battles) * 100 : 0;
  }
}
```

## ⚡ Real-Time Battle Interface

### Live Battle Component

```javascript
class LiveBattleInterface {
  constructor(containerElement) {
    this.container = containerElement;
    this.battle = null;
    this.isActive = false;
    
    this.elements = {
      battleArea: null,
      scoreBoard: null,
      audienceReaction: null,
      controls: null
    };
    
    this.initializeInterface();
  }

  initializeInterface() {
    this.container.innerHTML = `
      <div class="battle-arena">
        <div class="battle-header">
          <h2 id="battle-title">🎤 AI Rap Battle Arena</h2>
          <div id="battle-info" class="battle-info"></div>
        </div>
        
        <div class="participants-area">
          <div class="participant left" id="participant-1">
            <div class="participant-info"></div>
            <div class="verse-display"></div>
          </div>
          
          <div class="vs-indicator">VS</div>
          
          <div class="participant right" id="participant-2">
            <div class="participant-info"></div>
            <div class="verse-display"></div>
          </div>
        </div>
        
        <div class="battle-progress">
          <div id="round-indicator" class="round-indicator"></div>
          <div id="progress-bar" class="progress-bar"></div>
        </div>
        
        <div class="score-board" id="score-board">
          <div class="scores"></div>
        </div>
        
        <div class="audience-reaction" id="audience-reaction">
          <div class="crowd-energy"></div>
          <div class="reaction-messages"></div>
        </div>
        
        <div class="battle-controls" id="battle-controls">
          <button id="start-battle" class="primary">Start Battle</button>
          <button id="next-round" class="secondary" disabled>Next Round</button>
          <button id="stop-battle" class="danger" disabled>Stop Battle</button>
        </div>
      </div>
    `;
    
    this.bindEvents();
  }

  bindEvents() {
    document.getElementById('start-battle').addEventListener('click', () => this.startBattle());
    document.getElementById('next-round').addEventListener('click', () => this.nextRound());
    document.getElementById('stop-battle').addEventListener('click', () => this.stopBattle());
  }

  async startBattle(topic = 'artificial intelligence', participants = null) {
    if (!participants) {
      participants = [
        BattleParticipant.createClaude(),
        BattleParticipant.createGemini()
      ];
    }

    this.battle = new RapBattleEngine({
      topic: topic,
      maxRounds: 3,
      style: 'competitive'
    });

    // Add participants
    participants.forEach(p => this.battle.addParticipant(p));

    // Update UI
    this.updateBattleInfo(topic, participants);
    this.updateControls(true);
    
    // Start the battle
    this.isActive = true;
    await this.executeBattle();
  }

  async executeBattle() {
    const participants = Array.from(this.battle.participants.values());
    
    for (let round = 1; round <= this.battle.battleState.maxRounds; round++) {
      await this.executeRound(round, participants);
      
      if (round < this.battle.battleState.maxRounds) {
        await this.delay(2000); // Pause between rounds
      }
    }
    
    await this.declareBattleWinner();
    this.updateControls(false);
  }

  async executeRound(roundNumber, participants) {
    this.updateRoundIndicator(roundNumber);
    
    for (let i = 0; i < participants.length; i++) {
      const participant = participants[i];
      const opponent = participants[1 - i];
      
      // Generate verse
      this.showGeneratingIndicator(participant.id);
      
      const verse = await this.generateVerseForParticipant(participant, {
        round: roundNumber,
        topic: this.battle.battleState.topic,
        opponent: opponent,
        previousVerse: this.getLastOpponentVerse(opponent.id)
      });

      // Display verse with animation
      await this.displayVerse(participant.id, verse);
      
      // Get audience reaction
      const score = await this.scoreVerse(verse);
      const audienceReaction = await this.battle.audienceReaction.reactToVerse(verse, score);
      
      // Update displays
      this.updateScore(participant.id, score);
      this.showAudienceReaction(audienceReaction);
      
      // Pause for dramatic effect
      await this.delay(1500);
    }
  }

  async generateVerseForParticipant(participant, context) {
    const generator = new VerseGenerator();
    return await generator.generateVerse(participant, context);
  }

  async displayVerse(participantId, verse) {
    const verseElement = document.querySelector(`#participant-${participantId === 'claude' ? '1' : '2'} .verse-display`);
    
    // Clear previous verse
    verseElement.innerHTML = '';
    
    // Add verse with typewriter effect
    const lines = verse.text.split('\n');
    for (const line of lines) {
      const lineElement = document.createElement('div');
      lineElement.className = 'verse-line';
      verseElement.appendChild(lineElement);
      
      await this.typewriterEffect(lineElement, line);
      await this.delay(300); // Pause between lines
    }
    
    // Add highlighting effect
    verseElement.classList.add('verse-highlight');
    setTimeout(() => verseElement.classList.remove('verse-highlight'), 1000);
  }

  async typewriterEffect(element, text, speed = 50) {
    return new Promise(resolve => {
      let i = 0;
      const timer = setInterval(() => {
        if (i < text.length) {
          element.textContent += text.charAt(i);
          i++;
        } else {
          clearInterval(timer);
          resolve();
        }
      }, speed);
    });
  }

  showGeneratingIndicator(participantId) {
    const verseElement = document.querySelector(`#participant-${participantId === 'claude' ? '1' : '2'} .verse-display`);
    verseElement.innerHTML = '<div class="generating">🎤 Generating verse...</div>';
  }

  updateScore(participantId, score) {
    const scoreBoard = document.getElementById('score-board');
    const participantScore = document.querySelector(`#score-${participantId}`) || this.createScoreElement(participantId);
    
    participantScore.querySelector('.weighted-score').textContent = score.weightedScore.toFixed(1);
    
    // Update individual criteria scores
    Object.entries(score.scores).forEach(([criterion, value]) => {
      const criterionElement = participantScore.querySelector(`.${criterion}-score`);
      if (criterionElement) {
        criterionElement.textContent = value;
      }
    });
  }

  createScoreElement(participantId) {
    const scoreBoard = document.querySelector('#score-board .scores');
    const scoreElement = document.createElement('div');
    scoreElement.id = `score-${participantId}`;
    scoreElement.className = 'participant-score';
    scoreElement.innerHTML = `
      <h4>${participantId.toUpperCase()}</h4>
      <div class="main-score">
        <span class="weighted-score">0.0</span>
      </div>
      <div class="detailed-scores">
        <div class="wordplay-score">0</div>
        <div class="flow-score">0</div>
        <div class="relevance-score">0</div>
        <div class="originality-score">0</div>
        <div class="impact-score">0</div>
      </div>
    `;
    
    scoreBoard.appendChild(scoreElement);
    return scoreElement;
  }

  showAudienceReaction(reaction) {
    const reactionArea = document.getElementById('audience-reaction');
    const messagesElement = reactionArea.querySelector('.reaction-messages');
    const energyElement = reactionArea.querySelector('.crowd-energy');
    
    // Update energy bar
    energyElement.style.width = `${reaction.energyLevel}%`;
    energyElement.className = `crowd-energy ${reaction.crowdMood}`;
    
    // Show reaction messages
    messagesElement.innerHTML = '';
    reaction.messages.forEach((message, index) => {
      setTimeout(() => {
        const messageElement = document.createElement('span');
        messageElement.className = `reaction-message ${reaction.type}`;
        messageElement.textContent = message;
        messagesElement.appendChild(messageElement);
        
        // Remove message after animation
        setTimeout(() => messageElement.remove(), 2000);
      }, index * 200);
    });
  }

  updateRoundIndicator(round) {
    const indicator = document.getElementById('round-indicator');
    indicator.textContent = `Round ${round} / ${this.battle.battleState.maxRounds}`;
    
    const progressBar = document.getElementById('progress-bar');
    const progress = (round / this.battle.battleState.maxRounds) * 100;
    progressBar.style.width = `${progress}%`;
  }

  updateBattleInfo(topic, participants) {
    const infoElement = document.getElementById('battle-info');
    infoElement.innerHTML = `
      <div class="topic">Topic: ${topic}</div>
      <div class="participants">
        ${participants.map(p => `<span class="participant-tag">${p.name}</span>`).join(' vs ')}
      </div>
    `;
  }

  updateControls(battleActive) {
    document.getElementById('start-battle').disabled = battleActive;
    document.getElementById('next-round').disabled = !battleActive;
    document.getElementById('stop-battle').disabled = !battleActive;
  }

  async declareBattleWinner() {
    const winner = this.calculateBattleWinner();
    
    const winnerAnnouncement = document.createElement('div');
    winnerAnnouncement.className = 'battle-winner';
    winnerAnnouncement.innerHTML = `
      <h2>🏆 Battle Winner: ${winner.name}</h2>
      <div class="final-score">${winner.finalScore.toFixed(1)} / 10</div>
      <div class="winner-stats">
        Winning margin: ${winner.margin.toFixed(1)} points
      </div>
    `;
    
    this.container.appendChild(winnerAnnouncement);
    
    // Celebration effect
    this.triggerCelebration();
  }

  calculateBattleWinner() {
    const participants = Array.from(this.battle.participants.values());
    const scores = participants.map(p => ({
      ...p,
      finalScore: this.calculateFinalScore(p.id),
      totalVerses: p.verses.length
    }));
    
    const winner = scores.reduce((best, current) => 
      current.finalScore > best.finalScore ? current : best
    );
    
    const runnerUp = scores.find(p => p.id !== winner.id);
    winner.margin = winner.finalScore - runnerUp.finalScore;
    
    return winner;
  }

  calculateFinalScore(participantId) {
    // Calculate average score across all rounds
    const participantScores = this.battle.judging.scoringHistory
      .flatMap(round => round.scores)
      .filter(score => score.participant === participantId);
    
    if (participantScores.length === 0) return 0;
    
    const totalScore = participantScores.reduce((sum, score) => sum + score.weightedScore, 0);
    return totalScore / participantScores.length;
  }

  triggerCelebration() {
    // Add confetti or celebration animation
    const celebration = document.createElement('div');
    celebration.className = 'celebration-overlay';
    celebration.innerHTML = '🎉🎊🏆🎊🎉';
    
    this.container.appendChild(celebration);
    
    setTimeout(() => celebration.remove(), 3000);
  }

  async scoreVerse(verse) {
    const judge = new BattleJudge();
    return await judge.scoreVerse(verse, {
      topic: this.battle.battleState.topic,
      round: this.battle.battleState.currentRound
    });
  }

  getLastOpponentVerse(opponentId) {
    const opponentVerses = this.battle.history.filter(entry => entry.participant === opponentId);
    return opponentVerses.length > 0 ? opponentVerses[opponentVerses.length - 1].text : '';
  }

  async delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}
```

## 🎨 Styling and Animation

### CSS for Battle Interface

```css
.battle-arena {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Arial', sans-serif;
  background: linear-gradient(135deg, #1a1a2e, #16213e, #0f0f23);
  color: white;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.5);
}

.battle-header {
  text-align: center;
  margin-bottom: 30px;
}

.battle-header h2 {
  font-size: 2.5em;
  margin: 0;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
}

.participants-area {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 30px 0;
  min-height: 300px;
}

.participant {
  flex: 1;
  max-width: 45%;
  padding: 20px;
  border-radius: 10px;
  background: rgba(255,255,255,0.1);
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.participant.left {
  border-left: 4px solid #ff6b6b;
}

.participant.right {
  border-right: 4px solid #4ecdc4;
}

.vs-indicator {
  font-size: 3em;
  font-weight: bold;
  text-shadow: 2px 2px 8px rgba(0,0,0,0.7);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.verse-display {
  min-height: 150px;
  padding: 15px;
  background: rgba(0,0,0,0.3);
  border-radius: 8px;
  margin-top: 15px;
  font-family: 'Courier New', monospace;
  line-height: 1.6;
}

.verse-line {
  margin: 8px 0;
  opacity: 0;
  animation: fadeInUp 0.5s ease forwards;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.verse-highlight {
  animation: highlightFlash 1s ease;
}

@keyframes highlightFlash {
  0%, 100% { background: rgba(0,0,0,0.3); }
  50% { background: rgba(255,215,0,0.3); }
}

.generating {
  text-align: center;
  color: #ffd700;
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0.3; }
}

.battle-progress {
  margin: 30px 0;
  text-align: center;
}

.round-indicator {
  font-size: 1.5em;
  margin-bottom: 10px;
  color: #ffd700;
}

.progress-bar {
  height: 8px;
  background: #ffd700;
  border-radius: 4px;
  transition: width 0.5s ease;
  margin: 0 auto;
  max-width: 300px;
}

.score-board {
  margin: 30px 0;
  background: rgba(255,255,255,0.05);
  padding: 20px;
  border-radius: 10px;
}

.scores {
  display: flex;
  justify-content: space-around;
}

.participant-score {
  text-align: center;
  padding: 15px;
  border-radius: 8px;
  background: rgba(255,255,255,0.1);
}

.main-score {
  font-size: 2em;
  font-weight: bold;
  color: #ffd700;
  margin: 10px 0;
}

.detailed-scores {
  display: flex;
  gap: 10px;
  font-size: 0.9em;
  margin-top: 10px;
}

.audience-reaction {
  margin: 30px 0;
  text-align: center;
}

.crowd-energy {
  height: 20px;
  background: linear-gradient(90deg, #ff6b6b, #ffd700, #4ecdc4);
  border-radius: 10px;
  transition: width 0.5s ease;
  margin: 10px auto;
  max-width: 400px;
}

.crowd-energy.hyped {
  animation: energyPulse 0.5s infinite alternate;
}

@keyframes energyPulse {
  from { transform: scaleY(1); }
  to { transform: scaleY(1.2); }
}

.reaction-messages {
  height: 60px;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.reaction-message {
  padding: 5px 15px;
  border-radius: 20px;
  font-weight: bold;
  animation: reactionPop 2s ease;
}

.reaction-message.fire {
  background: #ff6b6b;
  color: white;
}

.reaction-message.clever {
  background: #4ecdc4;
  color: white;
}

.reaction-message.hype {
  background: #ffd700;
  color: black;
}

@keyframes reactionPop {
  0% { transform: scale(0); opacity: 0; }
  20% { transform: scale(1.2); opacity: 1; }
  80% { transform: scale(1); opacity: 1; }
  100% { transform: scale(0.8); opacity: 0; }
}

.battle-controls {
  text-align: center;
  margin-top: 30px;
}

.battle-controls button {
  padding: 12px 30px;
  margin: 0 10px;
  border: none;
  border-radius: 25px;
  font-size: 1.1em;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
}

.battle-controls button.primary {
  background: #4ecdc4;
  color: white;
}

.battle-controls button.secondary {
  background: #ffd700;
  color: black;
}

.battle-controls button.danger {
  background: #ff6b6b;
  color: white;
}

.battle-controls button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.3);
}

.battle-controls button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.battle-winner {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(0,0,0,0.9);
  padding: 40px;
  border-radius: 15px;
  text-align: center;
  z-index: 1000;
  animation: winnerReveal 1s ease;
}

@keyframes winnerReveal {
  from {
    opacity: 0;
    transform: translate(-50%, -50%) scale(0.5);
  }
  to {
    opacity: 1;
    transform: translate(-50%, -50%) scale(1);
  }
}

.celebration-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 5em;
  z-index: 999;
  pointer-events: none;
  animation: celebrate 3s ease;
}

@keyframes celebrate {
  0% { opacity: 0; transform: scale(0); }
  20% { opacity: 1; transform: scale(1.2); }
  80% { opacity: 1; transform: scale(1); }
  100% { opacity: 0; transform: scale(0.8); }
}
```

## 🚀 Usage Example

### Complete Implementation

```javascript
// Initialize the battle system
document.addEventListener('DOMContentLoaded', () => {
  const battleContainer = document.getElementById('battle-container');
  const battleInterface = new LiveBattleInterface(battleContainer);
  
  // Create custom participants
  const participants = [
    BattleParticipant.createClaude(),
    BattleParticipant.createGemini()
  ];
  
  // Start a battle
  battleInterface.startBattle('artificial intelligence evolution', participants);
});

// Example of starting different battle types
async function startCustomBattle(topic, style) {
  const battleInterface = new LiveBattleInterface(document.getElementById('battle-arena'));
  
  const participants = [
    new BattleParticipant({
      id: 'technical-ai',
      name: 'Technical AI',
      personality: 'technical_wordsmith',
      style: 'technical',
      specialties: ['complex_rhymes', 'technical_knowledge']
    }),
    new BattleParticipant({
      id: 'creative-ai',
      name: 'Creative AI',
      personality: 'creative_visual',
      style: 'artistic',
      specialties: ['storytelling', 'visual_metaphors']
    })
  ];
  
  await battleInterface.startBattle(topic, participants);
}
```

---

*This technical specification provides a complete framework for implementing AI-powered rap battles with real-time interaction, scoring, and audience simulation. The system is designed to be modular, extensible, and production-ready.*