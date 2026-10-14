import apiClient from './httpClient';

export const fetchFlowProjects = async () => {
  const { data } = await apiClient.get('/flow/projects');
  return data;
};

export const triggerSceneRender = async (projectId, sceneId) => {
  const { data } = await apiClient.post(`/flow/projects/${projectId}/scenes/${sceneId}/launch`);
  return data;
};

export const describeScene = async (projectId, sceneId) => {
  const { data } = await apiClient.post(`/flow/projects/${projectId}/scenes/${sceneId}/describe`);
  return data;
};
