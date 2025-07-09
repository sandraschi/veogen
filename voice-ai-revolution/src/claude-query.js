/**
 * 🔄 Claude Query Handler
 * Robust AI interaction with retries and error handling
 */

const ClaudeQuery = {
  defaultOptions: {
    maxRetries: 3,
    retryDelay: 1000,
    timeout: 30000,
    parseJSON: false
  },

  async queryWithRetry(prompt, options = {}) {
    const config = { ...this.defaultOptions, ...options };
    let lastError;

    for (let attempt = 1; attempt <= config.maxRetries; attempt++) {
      try {
        const response = await this.executeQuery(prompt, config);
        
        if (config.parseJSON) {
          return JSON.parse(response);
        }
        
        return response;
      } catch (error) {
        lastError = error;
        console.warn(`Query attempt ${attempt} failed:`, error.message);
        
        if (attempt < config.maxRetries) {
          await this.delay(config.retryDelay * attempt);
        }
      }
    }
    
    if (config.fallback !== undefined) {
      return config.fallback;
    }
    
    throw new Error(`Query failed after ${config.maxRetries} attempts: ${lastError.message}`);
  },

  async executeQuery(prompt, config) {
    return new Promise(async (resolve, reject) => {
      const timeoutId = setTimeout(() => {
        reject(new Error(`Query timeout after ${config.timeout}ms`));
      }, config.timeout);

      try {
        const response = await window.claude.complete(prompt);
        clearTimeout(timeoutId);
        resolve(response);
      } catch (error) {
        clearTimeout(timeoutId);
        reject(error);
      }
    });
  },

  async delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  },

  async batchProcess(prompts, options = {}) {
    const { concurrency = 3, delay = 500 } = options;
    const results = [];
    
    for (let i = 0; i < prompts.length; i += concurrency) {
      const batch = prompts.slice(i, i + concurrency);
      
      const batchResults = await Promise.allSettled(
        batch.map(prompt => this.queryWithRetry(prompt, options))
      );
      
      results.push(...batchResults);
      
      if (i + concurrency < prompts.length) {
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
    
    return results;
  }
};

export default ClaudeQuery;