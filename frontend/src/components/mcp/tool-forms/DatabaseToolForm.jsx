import {
  Code as CodeIcon,
  ContentCopy as ContentCopyIcon,
  ExpandLess as ExpandLessIcon,
  ExpandMore as ExpandMoreIcon,
  History as HistoryIcon,
  PlayArrow as PlayArrowIcon,
  PlayArrow as RunIcon,
  Save as SaveIcon,
  TableChart as TableChartIcon,
} from '@mui/icons-material';
import {
  Box,
  Button,
  Chip,
  CircularProgress,
  Collapse,
  Divider,
  FormControl,
  Grid,
  IconButton,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tabs,
  TextField,
  Tooltip,
  Typography,
} from '@mui/material';
import axios from 'axios';
import React, { useState, useEffect } from 'react';
import DatabaseConnectionManager from './DatabaseConnectionManager';

const DatabaseToolForm = ({ tool, showSnackbar }) => {
  // Form state
  const [formData, setFormData] = useState({
    connectionId: '',
    query: '',
    operation: 'query', // 'query', 'execute', 'tables', 'schema'
    parameters: '{}',
    limit: 100,
    saveAs: '',
  });

  // UI state
  const [connections, setConnections] = useState([]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [savingQuery, setSavingQuery] = useState(false);
  const [savedQueries, setSavedQueries] = useState([]);
  const [activeTab, setActiveTab] = useState('query');
  const [expandedQuery, setExpandedQuery] = useState(false);
  const [previewMode, setPreviewMode] = useState('table'); // 'table' or 'json'

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  // Load saved connections and queries
  const fetchConnections = async () => {
    try {
      const response = await axios.get('/api/mcp/execute', {
        params: {
          server: tool.server,
          tool: 'list_connections',
        },
      });
      setConnections(response.data.connections || []);
    } catch (err) {
      console.error('Error fetching connections:', err);
      showSnackbar('Failed to load database connections', 'error');
    }
  };

  const fetchSavedQueries = async () => {
    try {
      const response = await axios.get('/api/mcp/execute', {
        params: {
          server: tool.server,
          tool: 'list_saved_queries',
        },
      });
      setSavedQueries(response.data.queries || []);
    } catch (err) {
      console.error('Error fetching saved queries:', err);
      // Don't show error if the endpoint doesn't exist yet
      if (err.response?.status !== 404) {
        showSnackbar('Failed to load saved queries', 'error');
      }
    }
  };

  // Memoize the fetch functions to prevent infinite loops
  // biome-ignore lint/correctness/useExhaustiveDependencies: fetchConnections closes over tool.server and showSnackbar; they refresh the memoized copy
  const memoizedFetchConnections = React.useCallback(fetchConnections, [tool.server, showSnackbar]);
  // biome-ignore lint/correctness/useExhaustiveDependencies: fetchSavedQueries closes over tool.server and showSnackbar; they refresh the memoized copy
  const memoizedFetchSavedQueries = React.useCallback(fetchSavedQueries, [tool.server, showSnackbar]);

  useEffect(() => {
    memoizedFetchConnections();
    memoizedFetchSavedQueries();
  }, [memoizedFetchConnections, memoizedFetchSavedQueries]);

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!formData.connectionId) {
      showSnackbar('Please select a database connection', 'warning');
      return;
    }

    if (!formData.query.trim()) {
      showSnackbar('Please enter a query', 'warning');
      return;
    }

    setLoading(true);

    try {
      // Parse parameters if provided
      const params = {
        connection_id: formData.connectionId,
        query: formData.query,
        limit: formData.limit,
      };

      // Add parameters if provided and valid JSON
      if (formData.parameters?.trim()) {
        try {
          params.parameters = JSON.parse(formData.parameters);
        } catch (_err) {
          showSnackbar('Invalid JSON in parameters', 'error');
          return;
        }
      }

      // Determine the tool to use based on operation
      let toolName = 'execute_query';
      if (formData.operation === 'tables') {
        toolName = 'list_tables';
      } else if (formData.operation === 'schema') {
        toolName = 'get_schema';
      }

      const response = await axios.post('/api/mcp/execute', {
        server: tool.server,
        tool: toolName,
        params,
      });

      setResult(response.data);
      showSnackbar('Query executed successfully', 'success');
    } catch (error) {
      console.error('Database operation failed:', error);
      showSnackbar(`Error: ${error.response?.data?.detail || error.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  // Handle saving a query
  const handleSaveQuery = async () => {
    if (!formData.saveAs.trim()) {
      showSnackbar('Please enter a name for this query', 'warning');
      return;
    }

    setSavingQuery(true);

    try {
      await axios.post('/api/mcp/execute', {
        server: tool.server,
        tool: 'save_query',
        params: {
          name: formData.saveAs,
          query: formData.query,
          connection_id: formData.connectionId,
        },
      });

      showSnackbar('Query saved successfully', 'success');

      // Refresh saved queries
      const response = await axios.get('/api/mcp/execute', {
        params: {
          server: tool.server,
          tool: 'list_saved_queries',
        },
      });
      setSavedQueries(response.data.queries || []);
    } catch (error) {
      console.error('Error saving query:', error);
      showSnackbar(`Failed to save query: ${error.response?.data?.detail || error.message}`, 'error');
    } finally {
      setSavingQuery(false);
    }
  };

  // Load a saved query
  const loadSavedQuery = (query) => {
    setFormData((prev) => ({
      ...prev,
      query: query.sql,
      connectionId: query.connection_id || '',
      saveAs: query.name,
    }));
    setActiveTab('query');
    showSnackbar(`Loaded query: ${query.name}`, 'success');
  };

  // Copy query to clipboard
  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    showSnackbar('Copied to clipboard', 'success');
  };

  const renderResult = () => {
    if (!result) return null;

    if (previewMode === 'json' || !Array.isArray(result)) {
      return (
        <pre
          style={{
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-word',
            margin: 0,
            fontFamily: 'monospace',
            fontSize: '0.875rem',
            maxHeight: '400px',
            overflow: 'auto',
            padding: '8px',
            backgroundColor: 'rgba(0, 0, 0, 0.1)',
            borderRadius: '4px',
          }}
        >
          {JSON.stringify(result, null, 2)}
        </pre>
      );
    }

    // Render as table
    if (result.length === 0) return <Typography>No results found</Typography>;

    const columns = Object.keys(result[0]);

    return (
      <Box sx={{ width: '100%', overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              {columns.map((col) => (
                <th
                  key={col}
                  style={{
                    padding: '8px',
                    borderBottom: '1px solid rgba(224, 224, 224, 1)',
                    textAlign: 'left',
                    backgroundColor: 'rgba(0, 0, 0, 0.04)',
                  }}
                >
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {result.slice(0, formData.limit).map((row, rowIndex) => (
              // biome-ignore lint/suspicious/noArrayIndexKey: query result rows have no id; list is replaced wholesale, never reordered
              <tr key={rowIndex}>
                {columns.map((col) => (
                  <td
                    key={col}
                    style={{
                      padding: '8px',
                      borderBottom: '1px solid rgba(224, 224, 224, 0.5)',
                      verticalAlign: 'top',
                    }}
                  >
                    {typeof row[col] === 'object' ? JSON.stringify(row[col]) : String(row[col] ?? '')}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
        {result.length > formData.limit && (
          <Typography variant="caption" sx={{ display: 'block', mt: 1, textAlign: 'right' }}>
            Showing {formData.limit} of {result.length} rows
          </Typography>
        )}
      </Box>
    );
  };

  return (
    <Box sx={{ mt: 2 }}>
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={(_e, newValue) => setActiveTab(newValue)} aria-label="database tool tabs">
          <Tab label="Query" value="query" />
          <Tab label="Saved Queries" value="saved" />
          <Tab label="Connections" value="connections" />
        </Tabs>
      </Box>

      {/* Query Tab */}
      <Box sx={{ display: activeTab === 'query' ? 'block' : 'none' }}>
        <Box component="form" onSubmit={handleSubmit}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="h6" gutterBottom>
                  {tool.description || 'Database Query'}
                </Typography>
                <Box>
                  <Button
                    type="submit"
                    variant="contained"
                    color="primary"
                    disabled={loading || !formData.connectionId || !formData.query.trim()}
                    startIcon={loading ? <CircularProgress size={20} /> : <RunIcon />}
                    sx={{ mr: 1 }}
                  >
                    {loading ? 'Executing...' : 'Execute'}
                  </Button>

                  <Button
                    variant="outlined"
                    onClick={() => setExpandedQuery(!expandedQuery)}
                    endIcon={expandedQuery ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                    sx={{ mr: 1 }}
                  >
                    {expandedQuery ? 'Less Options' : 'More Options'}
                  </Button>
                </Box>
              </Box>
              <Divider sx={{ my: 2 }} />
            </Grid>

            <Grid item xs={12} md={6}>
              <FormControl fullWidth required>
                <InputLabel>Connection</InputLabel>
                <Select
                  name="connectionId"
                  value={formData.connectionId}
                  onChange={handleChange}
                  label="Connection"
                  disabled={loading}
                >
                  {connections.map((conn) => (
                    <MenuItem key={conn.id} value={conn.id}>
                      {conn.name} ({conn.type})
                    </MenuItem>
                  ))}
                  {connections.length === 0 && (
                    <MenuItem disabled>No connections found. Add one in the Connections tab.</MenuItem>
                  )}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={6}>
              <FormControl fullWidth disabled={loading}>
                <InputLabel>Operation</InputLabel>
                <Select name="operation" value={formData.operation} label="Operation" onChange={handleChange} required>
                  <MenuItem value="query">Run Query</MenuItem>
                  <MenuItem value="execute">Execute Command</MenuItem>
                  <MenuItem value="tables">List Tables</MenuItem>
                  <MenuItem value="schema">Get Schema</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            {(formData.operation === 'query' || formData.operation === 'execute') && (
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={expandedQuery ? 8 : 4}
                  label={formData.operation === 'query' ? 'SQL Query' : 'SQL Command'}
                  name="query"
                  value={formData.query}
                  onChange={handleChange}
                  disabled={loading}
                  required
                  placeholder={
                    formData.operation === 'query'
                      ? 'SELECT * FROM table_name WHERE condition = :param'
                      : 'UPDATE table_name SET column = value WHERE condition'
                  }
                  InputProps={{
                    style: { fontFamily: 'monospace', fontSize: '0.9rem' },
                  }}
                />
              </Grid>
            )}

            <Collapse in={expandedQuery} timeout="auto" unmountOnExit>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  label="Parameters (JSON)"
                  name="parameters"
                  value={formData.parameters}
                  onChange={handleChange}
                  disabled={loading}
                  helperText="JSON object of parameters for parameterized queries"
                  InputProps={{
                    style: { fontFamily: 'monospace', fontSize: '0.9rem' },
                  }}
                />
              </Grid>

              <Grid item xs={12}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <TextField
                    fullWidth
                    label="Save query as"
                    name="saveAs"
                    value={formData.saveAs}
                    onChange={handleChange}
                    disabled={loading || savingQuery}
                    placeholder="My Saved Query"
                  />
                  <Button
                    variant="outlined"
                    startIcon={savingQuery ? <CircularProgress size={20} /> : <SaveIcon />}
                    onClick={handleSaveQuery}
                    disabled={!formData.saveAs.trim() || !formData.query.trim() || savingQuery}
                    sx={{ whiteSpace: 'nowrap' }}
                  >
                    {savingQuery ? 'Saving...' : 'Save Query'}
                  </Button>
                </Box>
              </Grid>
            </Collapse>
          </Grid>
        </Box>

        {/* Results Section */}
        {result && (
          <Box sx={{ mt: 4 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
              <Typography variant="subtitle1">Results</Typography>
              <Button
                variant="outlined"
                size="small"
                onClick={() => setPreviewMode((prev) => (prev === 'table' ? 'json' : 'table'))}
                startIcon={previewMode === 'table' ? <CodeIcon /> : <TableChartIcon />}
              >
                {previewMode === 'table' ? 'View as JSON' : 'View as Table'}
              </Button>
            </Box>

            {renderResult()}
          </Box>
        )}
      </Box>

      {/* Saved Queries Tab */}
      <Box sx={{ display: activeTab === 'saved' ? 'block' : 'none' }}>
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Saved Queries
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Select a query to load it into the editor
          </Typography>

          {savedQueries.length === 0 ? (
            <Paper sx={{ p: 3, textAlign: 'center' }}>
              <Typography variant="body1" color="text.secondary">
                No saved queries found. Save a query in the Query tab.
              </Typography>
            </Paper>
          ) : (
            <TableContainer component={Paper}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Name</TableCell>
                    <TableCell>Query</TableCell>
                    <TableCell>Connection</TableCell>
                    <TableCell>Last Used</TableCell>
                    <TableCell align="right">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {savedQueries.map((query) => (
                    <TableRow
                      key={query.id}
                      hover
                      sx={{ '&:hover': { cursor: 'pointer' } }}
                      onClick={() => loadSavedQuery(query)}
                    >
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <HistoryIcon color="action" sx={{ mr: 1 }} />
                          <Typography variant="body2">{query.name}</Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Typography
                          variant="caption"
                          sx={{
                            fontFamily: 'monospace',
                            display: '-webkit-box',
                            WebkitLineClamp: 1,
                            WebkitBoxOrient: 'vertical',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            maxWidth: '300px',
                          }}
                        >
                          {query.sql}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip label={query.connection_name || 'Default'} size="small" variant="outlined" />
                      </TableCell>
                      <TableCell>{query.last_used ? new Date(query.last_used).toLocaleString() : 'Never'}</TableCell>
                      <TableCell align="right">
                        <Tooltip title="Load Query">
                          <IconButton
                            size="small"
                            onClick={(e) => {
                              e.stopPropagation();
                              loadSavedQuery(query);
                            }}
                          >
                            <PlayArrowIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Copy to Clipboard">
                          <IconButton
                            size="small"
                            onClick={(e) => {
                              e.stopPropagation();
                              copyToClipboard(query.sql);
                            }}
                          >
                            <ContentCopyIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </Box>
      </Box>

      {/* Connections Tab */}
      <Box sx={{ display: activeTab === 'connections' ? 'block' : 'none' }}>
        <DatabaseConnectionManager server={tool.server} showSnackbar={showSnackbar} />
      </Box>
    </Box>
  );
};

export default DatabaseToolForm;
