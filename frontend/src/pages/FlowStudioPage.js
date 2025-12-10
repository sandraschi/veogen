import React, { useMemo, useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import {
  fetchFlowProjects,
  triggerSceneRender,
  describeScene,
} from '../services/flowService';

const FlowStudioPage = () => {
  const queryClient = useQueryClient();
  const [selectedProjectId, setSelectedProjectId] = useState(null);
  const { data: projects = [], isLoading } = useQuery(['flow-projects'], fetchFlowProjects, {
    enabled: true,
    refetchInterval: 60000,
  });

  const selectedProject = useMemo(
    () => projects.find((project) => project.id === selectedProjectId) || projects[0],
    [projects, selectedProjectId]
  );

  const launchMutation = useMutation(
    ({ projectId, sceneId }) => triggerSceneRender(projectId, sceneId),
    {
      onSuccess: () => {
        toast.success('Render started');
        queryClient.invalidateQueries(['flow-projects']);
      },
      onError: (error) => toast.error(error.response?.data?.detail || 'Failed to launch render'),
    }
  );

  const describeMutation = useMutation(
    ({ projectId, sceneId }) => describeScene(projectId, sceneId),
    {
      onSuccess: (data) => toast.success(`Caption ready: ${data.caption.slice(0, 40)}...`),
      onError: (error) => toast.error(error.response?.data?.detail || 'Caption failed'),
    }
  );

  if (isLoading) {
    return <div className="p-6 text-white">Loading Flow projects...</div>;
  }

  if (!projects.length) {
    return <div className="p-6 text-white">No Flow projects synced yet.</div>;
  }

  return (
    <div className="p-6 space-y-6">
      <header className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white">Flow Studio</h1>
          <p className="text-gray-400">
            Manage Flow scenes, launch renders, and keep approvals on track.
          </p>
        </div>
        <select
          value={selectedProject?.id}
          onChange={(event) => setSelectedProjectId(event.target.value)}
          className="bg-gray-900 border border-gray-700 text-white rounded-lg px-4 py-2"
        >
          {projects.map((project) => (
            <option key={project.id} value={project.id}>
              {project.title}
            </option>
          ))}
        </select>
      </header>

      <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
        <aside className="xl:col-span-1 bg-gray-900/70 border border-gray-800 rounded-2xl p-4 space-y-4">
          <h2 className="text-white font-semibold">Ingredients</h2>
          <p className="text-sm text-gray-400">
            Flow ingredients sync automatically; attach them while editing scenes.
          </p>
          <ul className="space-y-2 max-h-[60vh] overflow-y-auto">
            {(selectedProject?.ingredients || []).map((ingredient) => (
              <li key={ingredient.id} className="p-3 rounded-xl bg-gray-800/60 text-white text-sm">
                <p className="font-semibold">{ingredient.name}</p>
                <p className="text-gray-400 text-xs capitalize">{ingredient.ingredient_type}</p>
              </li>
            ))}
            {!selectedProject?.ingredients?.length && (
              <li className="text-gray-500 text-sm">Sync Flow to see ingredients.</li>
            )}
          </ul>
        </aside>

        <section className="xl:col-span-3 space-y-4">
          {(selectedProject?.scenes || []).map((scene) => (
            <div
              key={scene.id}
              className="bg-gray-900/80 border border-gray-800 rounded-2xl p-4 flex flex-col md:flex-row gap-4"
            >
              <div className="flex-1 space-y-2">
                <div className="flex items-center justify-between">
                  <h3 className="text-white font-semibold">
                    #{scene.order_index + 1} {scene.title}
                  </h3>
                  <span className="text-xs px-3 py-1 rounded-full bg-purple-500/20 text-purple-200 capitalize">
                    {scene.status}
                  </span>
                </div>
                <p className="text-gray-400 text-sm">{scene.prompt || 'No prompt synced yet.'}</p>
                <div className="flex flex-wrap gap-3 text-xs text-gray-400">
                  <span>Duration: {scene.duration_seconds}s</span>
                  <span>Aspect: {scene.aspect_ratio}</span>
                  <span>Style: {scene.style}</span>
                </div>

                <div className="flex flex-wrap gap-2 mt-4">
                  <button
                    onClick={() =>
                      launchMutation.mutate({ projectId: selectedProject.id, sceneId: scene.id })
                    }
                    className="px-4 py-2 rounded-lg bg-gradient-to-r from-purple-500 to-pink-500 text-white text-sm"
                  >
                    Launch Render
                  </button>
                  <button
                    onClick={() =>
                      describeMutation.mutate({ projectId: selectedProject.id, sceneId: scene.id })
                    }
                    className="px-4 py-2 rounded-lg border border-gray-700 text-sm text-gray-200"
                  >
                    Describe Scene
                  </button>
                </div>
              </div>

              <div className="md:w-64 space-y-3">
                {scene.poster_frame_url ? (
                  <img
                    src={scene.poster_frame_url}
                    alt={scene.title}
                    className="w-full h-36 object-cover rounded-xl border border-gray-800"
                  />
                ) : (
                  <div className="w-full h-36 rounded-xl border border-dashed border-gray-700 text-gray-500 flex items-center justify-center text-sm">
                    No frame
                  </div>
                )}
                <div className="bg-gray-800/80 rounded-xl p-3 text-xs text-gray-300 space-y-1">
                  <p className="font-semibold text-white">Approval Checklist</p>
                  <ul className="space-y-1">
                    {['promptFinalized', 'synthId', 'captions', 'audio'].map((key) => (
                      <li key={key} className="flex items-center gap-2">
                        <span
                          className={`w-2.5 h-2.5 rounded-full ${
                            scene.checklist[key] ? 'bg-green-400' : 'bg-gray-600'
                          }`}
                        />
                        <span className="capitalize">{key}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <div className="bg-gray-800/80 rounded-xl p-3 text-xs text-gray-300 space-y-1">
                  <p className="font-semibold text-white">Captions</p>
                  {scene.captions?.length ? (
                    <ul className="space-y-1">
                      {scene.captions.map((caption, index) => (
                        <li key={index} className="text-gray-400">
                          {caption}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-gray-500">Generate a caption to populate accessibility notes.</p>
                  )}
                </div>
              </div>
            </div>
          ))}
        </section>
      </div>
    </div>
  );
};

export default FlowStudioPage;

