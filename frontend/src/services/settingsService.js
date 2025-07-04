// Settings Service for User Preferences

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:4700';

class SettingsService {
  constructor() {
    this.settings = null;
  }

  async getSettings() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/settings`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          // Add authorization header when auth is implemented
          // 'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const settings = await response.json();
      this.settings = settings;
      return settings;
    } catch (error) {
      console.error('Failed to get settings:', error);
      // Return default settings if API fails
      return {
        google_api_key: '',
        google_cloud_project: '',
        gemini_api_key: '',
        default_style: 'cinematic',
        default_duration: 5,
        default_aspect_ratio: '16:9',
        auto_save: true,
        notifications: true,
        theme: 'dark'
      };
    }
  }

  async updateSettings(settingsData) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/settings`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // Add authorization header when auth is implemented
          // 'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(settingsData)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const updatedSettings = await response.json();
      this.settings = updatedSettings;
      return updatedSettings;
    } catch (error) {
      console.error('Failed to update settings:', error);
      throw error;
    }
  }

  async getSetting(key) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/settings/${key}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          // Add authorization header when auth is implemented
          // 'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`Failed to get setting ${key}:`, error);
      throw error;
    }
  }

  async setSetting(key, value, type = 'string') {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/settings/${key}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // Add authorization header when auth is implemented
          // 'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ value, type })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`Failed to set setting ${key}:`, error);
      throw error;
    }
  }

  // Get cached settings if available
  getCachedSettings() {
    return this.settings;
  }

  // Clear cached settings
  clearCache() {
    this.settings = null;
  }
}

export const settingsService = new SettingsService(); 