import apiClient from './httpClient';

export const startPromptCoachSession = async () => {
  const { data } = await apiClient.post('/prompt-coach/session');
  return data.session_id;
};

export const critiquePrompt = async (sessionId, prompt) => {
  const { data } = await apiClient.post('/prompt-coach/critique', {
    session_id: sessionId,
    prompt,
  });
  return data;
};

