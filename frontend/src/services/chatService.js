// Chat Service for AI Personas

const API_BASE_URL = 'http://localhost:11150';

const buildHeaders = (token, extraHeaders = {}) => {
  const headers = {
    'Content-Type': 'application/json',
    ...extraHeaders
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  return headers;
};

class ChatService {
  constructor() {
    this.conversations = new Map(); // Client-side cache for quick access
  }

  async startConversation(personaId, initialMessage, token, context = {}) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/chat/start`, {
        method: 'POST',
        headers: buildHeaders(token),
        body: JSON.stringify({
          persona_id: personaId,
          initial_message: initialMessage,
          context
        })
      });

      if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}));
        throw new Error(errorBody.detail || `Failed to start conversation (${response.status})`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to start conversation:', error);
      throw error;
    }
  }

  async sendMessage(conversationId, message, token, messageType = 'text') {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/chat/${conversationId}/message`, {
        method: 'POST',
        headers: buildHeaders(token),
        body: JSON.stringify({
          message,
          message_type: messageType
        })
      });

      if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}));
        throw new Error(errorBody.detail || `Failed to send message (${response.status})`);
      }

      return await response.json();
    } catch (error) {
      console.error('Chat message failed:', error);
      throw error;
    }
  }

  async getPersonas() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/chat/personas`);
      
      if (!response.ok) {
        throw new Error(`Failed to load personas (${response.status})`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to get personas:', error);
      throw error;
    }
  }

  async getConversations(token) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/chat/conversations`, {
        headers: buildHeaders(token, { 'Content-Type': 'application/json' })
      });

      if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}));
        throw new Error(errorBody.detail || `Failed to fetch conversations (${response.status})`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to get conversations:', error);
      throw error;
    }
  }

  async getConversationHistory(conversationId, token) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/chat/${conversationId}/history`, {
        headers: buildHeaders(token, { 'Content-Type': 'application/json' })
      });

      if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}));
        throw new Error(errorBody.detail || `Failed to load conversation history (${response.status})`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to get conversation history:', error);
      throw error;
    }
  }

  async deleteConversation(conversationId, token) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/chat/${conversationId}`, {
        method: 'DELETE',
        headers: buildHeaders(token, { 'Content-Type': 'application/json' })
      });

      if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}));
        throw new Error(errorBody.detail || `Failed to delete conversation (${response.status})`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to delete conversation:', error);
      throw error;
    }
  }

  async exportConversation(conversationId, format = 'json', token) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/chat/conversations/${conversationId}/export?format=${format}`, {
        headers: buildHeaders(token, { 'Content-Type': 'application/json' })
      });

      if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}));
        throw new Error(errorBody.detail || `Failed to export conversation (${response.status})`);
      }

      if (format === 'json') {
        return await response.json();
      } else {
        return await response.text();
      }
    } catch (error) {
      console.error('Failed to export conversation:', error);
      throw error;
    }
  }

  async regenerateResponse(conversationId, messageId, token) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/chat/conversations/${conversationId}/messages/${messageId}/regenerate`, {
        method: 'POST',
        headers: buildHeaders(token)
      });

      if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}));
        throw new Error(errorBody.detail || `Failed to regenerate response (${response.status})`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to regenerate response:', error);
      throw error;
    }
  }

  // Client-side conversation management helpers
  saveConversationLocally(conversationId, messages) {
    this.conversations.set(conversationId, {
      id: conversationId,
      messages: [...messages],
      lastUpdated: new Date()
    });
  }

  getLocalConversation(conversationId) {
    return this.conversations.get(conversationId);
  }

  getAllLocalConversations() {
    return Array.from(this.conversations.values());
  }

  clearLocalConversations() {
    this.conversations.clear();
  }
}

export const chatService = new ChatService();
