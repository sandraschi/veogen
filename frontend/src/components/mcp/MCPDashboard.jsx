import { Refresh as RefreshIcon } from '@mui/icons-material';
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Divider,
  Grid,
  IconButton,
  Paper,
  Snackbar,
  Tab,
  Tabs,
  Tooltip,
  Typography,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import axios from 'axios';
import React, { useState, useEffect, useCallback } from 'react';

// Tool Forms - Dynamic imports with error boundaries
const ToolFormWrapper = ({ toolType, ...props }) => {
  const [FormComponent, setFormComponent] = React.useState(null);
  const [error, setError] = React.useState(null);

  React.useEffect(() => {
    const loadComponent = async () => {
      try {
        // Try to import the component
        const module = await import(`./tool-forms/${toolType}Form.jsx`);
        setFormComponent(() => module.default);
        setError(null);
      } catch (err) {
        console.error(`Failed to load tool form: ${toolType}`, err);
        setError(`Tool form ${toolType} not available`);
      }
    };

    loadComponent();
  }, [toolType]);

  if (error) {
    return (
      <div className="p-4 bg-gray-800 rounded-lg">
        <h3 className="text-lg font-medium text-white mb-2">Tool Unavailable</h3>
        <p className="text-gray-300">{error}</p>
      </div>
    );
  }

  if (!FormComponent) {
    return <div className="p-4">Loading tool form...</div>;
  }

  return <FormComponent {...props} />;
};

const StyledPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  marginTop: theme.spacing(2),
  backgroundColor: theme.palette.background.paper,
}));

const ToolContainer = styled(Box)({
  marginTop: '1rem',
  '& > *': {
    margin: '0.5rem 0',
  },
});

const MCPDashboard = () => {
  const [servers, setServers] = useState([]);
  const [activeTab, setActiveTab] = useState(0);
  const [activeToolIndex, setActiveToolIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });

  const showSnackbar = useCallback((message, severity = 'info') => {
    setSnackbar({ open: true, message, severity });
  }, []);

  const fetchMCPServers = useCallback(
    async (showLoading = true) => {
      try {
        if (showLoading) {
          setLoading(true);
        } else {
          setRefreshing(true);
        }

        const response = await axios.get('/api/mcp/servers');
        setServers(response.data);
        setError(null);

        if (!showLoading) {
          showSnackbar('MCP servers refreshed successfully', 'success');
        }
      } catch (err) {
        console.error('Error fetching MCP servers:', err);
        setError('Failed to load MCP servers. Please check the console for details.');
        showSnackbar('Error loading MCP servers', 'error');
      } finally {
        setLoading(false);
        setRefreshing(false);
      }
    },
    [showSnackbar],
  );

  useEffect(() => {
    fetchMCPServers();
  }, [fetchMCPServers]);

  const handleCloseSnackbar = () => {
    setSnackbar((prev) => ({ ...prev, open: false }));
  };

  const handleTabChange = (_event, newValue) => {
    setActiveTab(newValue);
  };

  const handleRefresh = () => {
    fetchMCPServers(false);
  };

  const renderServerTab = (server, index) => {
    if (loading) return <CircularProgress />;
    if (error) return <Typography color="error">{error}</Typography>;

    const toolCount = server.tools?.length || 0;
    const statusColor = server.status === 'connected' ? 'success.main' : 'error.main';

    return (
      <Tab
        key={index}
        label={
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Box
              sx={{
                width: 10,
                height: 10,
                borderRadius: '50%',
                bgcolor: statusColor,
                mr: 1,
              }}
            />
            {server.name}
            <Box component="span" sx={{ ml: 1, color: 'text.secondary' }}>
              ({toolCount} {toolCount === 1 ? 'tool' : 'tools'})
            </Box>
          </Box>
        }
      />
    );
  };

  const renderToolForm = (tool) => {
    if (!tool) return null;

    // Map specific tool names to their form components
    const toolMappings = {
      // File Operations
      list_directory: 'Directory',
      list_files: 'Directory',
      read_file: 'File',
      write_file: 'File',
      append_file: 'File',
      delete_file: 'File',
      file: 'File',

      // Shell/Command Operations
      execute_command: 'Shell',
      run_command: 'Shell',
      shell: 'Shell',
      cmd: 'Shell',
      terminal: 'Shell',

      // Email Operations
      send_email: 'Email',
      email: 'Email',
      send_mail: 'Email',
      mail: 'Email',

      // Database Operations
      db_query: 'Database',
      db_execute: 'Database',
      database: 'Database',
      sql: 'Database',
      postgres: 'Database',
      mysql: 'Database',
      sqlite: 'Database',
      mssql: 'Database',

      // System Operations
      system_info: 'Generic',
      process: 'Generic',
      service: 'Generic',
    };

    const toolType = toolMappings[tool.name] || 'Generic';

    return <ToolFormWrapper toolType={toolType} tool={tool} showSnackbar={showSnackbar} />;
  };

  return (
    <Box sx={{ width: '100%' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h4">MCP Server Dashboard</Typography>
        <Tooltip title="Refresh MCP Servers">
          <IconButton onClick={handleRefresh} disabled={refreshing} color="primary" aria-label="refresh">
            <RefreshIcon className={refreshing ? 'spin' : ''} />
          </IconButton>
        </Tooltip>
      </Box>

      <StyledPaper>
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          variant="scrollable"
          scrollButtons="auto"
          aria-label="MCP Server Tabs"
        >
          {servers.map((server, index) => renderServerTab(server, index))}
        </Tabs>

        <Box sx={{ p: 3 }}>
          {servers[activeTab]?.tools?.length > 0 ? (
            <Grid container spacing={3}>
              <Grid item xs={12} sm={4} md={3}>
                <Tabs
                  orientation="vertical"
                  variant="scrollable"
                  value={activeToolIndex}
                  onChange={(_e, newValue) => setActiveToolIndex(newValue)}
                  sx={{ borderRight: 1, borderColor: 'divider' }}
                >
                  {servers[activeTab].tools.map((tool) => (
                    <Tab
                      key={tool.name}
                      label={
                        <Box sx={{ textAlign: 'left', width: '100%' }}>
                          <Typography noWrap>{tool.name}</Typography>
                          {tool.description && (
                            <Typography
                              variant="caption"
                              color="textSecondary"
                              noWrap
                              sx={{ display: 'block', width: '100%' }}
                            >
                              {tool.description}
                            </Typography>
                          )}
                        </Box>
                      }
                      sx={{
                        alignItems: 'flex-start',
                        textTransform: 'none',
                        minHeight: 'auto',
                        py: 1.5,
                        px: 2,
                        borderBottom: '1px solid',
                        borderColor: 'divider',
                        '&:last-child': {
                          borderBottom: 'none',
                        },
                      }}
                    />
                  ))}
                </Tabs>
              </Grid>

              <Grid item xs={12} sm={8} md={9}>
                <ToolContainer>
                  <Box sx={{ mb: 3 }}>
                    <Typography variant="h5" gutterBottom>
                      {servers[activeTab].tools[activeToolIndex]?.name}
                    </Typography>
                    <Typography variant="body1" color="textSecondary" paragraph>
                      {servers[activeTab].tools[activeToolIndex]?.description || 'No description available'}
                    </Typography>
                    <Divider sx={{ my: 2 }} />
                  </Box>

                  {renderToolForm(servers[activeTab].tools[activeToolIndex])}
                </ToolContainer>
              </Grid>
            </Grid>
          ) : (
            <Box
              sx={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                minHeight: '300px',
                textAlign: 'center',
                p: 3,
              }}
            >
              {servers[activeTab]?.status === 'error' ? (
                <>
                  <Typography variant="h6" color="error" gutterBottom>
                    Connection Error
                  </Typography>
                  <Typography color="textSecondary" paragraph>
                    Unable to connect to {servers[activeTab]?.name}. Please check if the server is running.
                  </Typography>
                  <Button
                    variant="outlined"
                    color="primary"
                    onClick={handleRefresh}
                    startIcon={<RefreshIcon />}
                    disabled={refreshing}
                  >
                    Retry Connection
                  </Button>
                </>
              ) : (
                <>
                  <Typography variant="h6" color="textSecondary" gutterBottom>
                    No Tools Available
                  </Typography>
                  <Typography color="textSecondary" paragraph>
                    This MCP server doesn't expose any tools or the connection failed.
                  </Typography>
                </>
              )}
            </Box>
          )}
        </Box>
      </StyledPaper>

      <Snackbar open={snackbar.open} autoHideDuration={6000} onClose={handleCloseSnackbar}>
        <Alert onClose={handleCloseSnackbar} severity={snackbar.severity}>
          {snackbar.message}
        </Alert>
      </Snackbar>

      <style jsx global>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        .spin {
          animation: spin 1s linear infinite;
        }
      `}</style>
    </Box>
  );
};

export default MCPDashboard;
