import apiClient from './httpClient';

export const importBriefToFlow = async (title, outline) => {
  const { data } = await apiClient.post('/workspace/flow/import', {
    title,
    outline,
  });
  return data;
};
