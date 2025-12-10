import apiClient from './httpClient';

export const generateSoundEffect = async (payload) => {
  const { data } = await apiClient.post('/sound-design/generate', payload);
  return data;
};

