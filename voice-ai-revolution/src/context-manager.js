/**
 * 🧠 Context Manager
 * User session and conversation state management
 */

class ContextManager {
  constructor(maxHistory = 10) {
    this.contexts = new Map();
    this.maxHistory = maxHistory;
  }

  createContext(contextId, initialData = {}) {
    this.contexts.set(contextId, {
      id: contextId,
      created: Date.now(),
      updated: Date.now(),
      data: initialData,
      history: [],
      metadata: {
        totalQueries: 0,
        successfulQueries: 0
      }
    });
  }

  updateContext(contextId, newData) {
    const context = this.contexts.get(contextId);
    if (!context) throw new Error(`Context '${contextId}' not found`);
    
    // Add to history
    context.history.push({
      timestamp: Date.now(),
      data: { ...context.data }
    });
    
    // Limit history size
    if (context.history.length > this.maxHistory) {
      context.history.shift();
    }
    
    // Update data
    Object.assign(context.data, newData);
    context.updated = Date.now();
  }

  async queryWithContext(contextId, prompt, updateData = {}) {
    const context = this.contexts.get(contextId);
    if (!context) throw new Error(`Context '${contextId}' not found`);
    
    const contextualPrompt = this.buildContextualPrompt(context, prompt);
    
    try {
      const response = await window.claude.complete(contextualPrompt);
      
      // Update context
      this.updateContext(contextId, {
        lastQuery: prompt,
        lastResponse: response,
        ...updateData
      });
      
      context.metadata.totalQueries++;
      context.metadata.successfulQueries++;
      
      return response;
    } catch (error) {
      context.metadata.totalQueries++;
      throw error;
    }
  }

  buildContextualPrompt(context, prompt) {
    const recentHistory = context.history.slice(-3).map(h => ({
      query: h.data.lastQuery,
      response: h.data.lastResponse?.substring(0, 100) + '...'
    }));
    
    return `
Context: ${JSON.stringify({
  user: context.data.user || 'User',
  preferences: context.data.preferences || {},
  recentHistory
})}

Current request: ${prompt}

Respond considering the context and user preferences.
    `.trim();
  }

  getContext(contextId) {
    return this.contexts.get(contextId);
  }

  clearContext(contextId) {
    this.contexts.delete(contextId);
  }

  exportContext(contextId) {
    const context = this.contexts.get(contextId);
    return context ? JSON.stringify(context, null, 2) : null;
  }
}

export default ContextManager;