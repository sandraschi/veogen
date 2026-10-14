import { ipcRenderer } from 'electron';
import { useCallback, useEffect, useState } from 'react';

const useMCPClient = () => {
  const [servers, setServers] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeServer, setActiveServer] = useState(null);
  const [availableTools, setAvailableTools] = useState({});

  // Initialize MCP client
  const initialize = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      // Request the main process to start MCP servers
      const servers = await ipcRenderer.invoke('mcp:start-servers');
      setServers(servers);

      // Discover available tools from all servers
      const tools = {};
      for (const [serverName, _server] of Object.entries(servers)) {
        try {
          const serverTools = await ipcRenderer.invoke('mcp:list-tools', serverName);
          tools[serverName] = serverTools;
        } catch (err) {
          console.error(`Failed to get tools from ${serverName}:`, err);
          tools[serverName] = [];
        }
      }

      setAvailableTools(tools);

      // Set the first available server as active
      const firstServer = Object.keys(servers)[0];
      if (firstServer) {
        setActiveServer(firstServer);
      }

      return servers;
    } catch (err) {
      console.error('Failed to initialize MCP client:', err);
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Execute a tool
  const executeTool = useCallback(
    async (toolName, params = {}) => {
      if (!activeServer) {
        throw new Error('No active MCP server selected');
      }

      try {
        setIsLoading(true);
        const result = await ipcRenderer.invoke('mcp:execute-tool', {
          server: activeServer,
          tool: toolName,
          params,
        });
        return result;
      } catch (err) {
        console.error(`Error executing tool ${toolName}:`, err);
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [activeServer],
  );

  // Clean up on unmount
  useEffect(() => {
    return () => {
      // Clean up MCP servers when component unmounts
      ipcRenderer.invoke('mcp:stop-servers').catch(console.error);
    };
  }, []);

  return {
    servers,
    availableTools,
    activeServer,
    setActiveServer,
    isLoading,
    error,
    initialize,
    executeTool,
  };
};

export default useMCPClient;
