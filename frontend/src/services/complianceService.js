import apiClient from './httpClient';

export const runSynthIdAudit = async () => {
  const { data } = await apiClient.post('/compliance/synthid/audit');
  return data;
};

