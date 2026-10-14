import {
  Add as AddIcon,
  CheckCircle as CheckCircleIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Error as ErrorIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import {
  Box,
  Button,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  Grid,
  IconButton,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Tooltip,
  Typography,
} from '@mui/material';
import axios from 'axios';
import React, { useState, useEffect } from 'react';

const DatabaseConnectionManager = ({ server, showSnackbar }) => {
  const [connections, setConnections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  // Error state is handled by the parent component through showSnackbar
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingId, setEditingId] = useState(null);

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    type: 'postgresql',
    host: 'localhost',
    port: '',
    database: '',
    username: '',
    password: '',
    options: '{}',
  });

  // Fetch connections from the server
  const fetchConnections = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/mcp/execute', {
        params: {
          server,
          tool: 'list_connections',
        },
      });
      setConnections(response.data.connections || []);
    } catch (err) {
      console.error('Error fetching connections:', err);
      showSnackbar('Failed to load database connections', 'error');
    } finally {
      setLoading(false);
    }
  };

  // Load connections on component mount
  const memoizedFetchConnections = React.useCallback(async () => {
    try {
      const response = await axios.get('/api/mcp/execute', {
        params: {
          server,
          tool: 'list_connections',
        },
      });
      setConnections(response.data.connections || []);
    } catch (err) {
      console.error('Error fetching connections:', err);
      showSnackbar('Failed to load database connections', 'error');
    }
  }, [server, showSnackbar]);

  useEffect(() => {
    memoizedFetchConnections();
  }, [memoizedFetchConnections]);

  // Handle form input changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);

    try {
      const toolName = editingId ? 'update_connection' : 'add_connection';
      const params = { ...formData };

      if (editingId) {
        params.connection_id = editingId;
      }

      // The response is not used, but we still want to await the request
      await axios.post('/api/mcp/execute', {
        server,
        tool: toolName,
        params,
      });

      showSnackbar(editingId ? 'Connection updated successfully' : 'Connection added successfully', 'success');

      setDialogOpen(false);
      fetchConnections();
    } catch (err) {
      console.error('Error saving connection:', err);
      showSnackbar(`Failed to save connection: ${err.response?.data?.detail || err.message}`, 'error');
    } finally {
      setSaving(false);
    }
  };

  // Handle connection test
  const testConnection = async (connectionId) => {
    try {
      await axios.post('/api/mcp/execute', {
        server,
        tool: 'test_connection',
        params: { connection_id: connectionId },
      });
      showSnackbar('Connection test successful', 'success');
      return true;
    } catch (err) {
      console.error('Connection test failed:', err);
      showSnackbar(`Connection test failed: ${err.response?.data?.detail || err.message}`, 'error');
      return false;
    }
  };

  // Handle connection deletion
  const deleteConnection = async (connectionId) => {
    if (!window.confirm('Are you sure you want to delete this connection?')) {
      return;
    }

    try {
      await axios.post('/api/mcp/execute', {
        server,
        tool: 'remove_connection',
        params: { connection_id: connectionId },
      });

      showSnackbar('Connection deleted successfully', 'success');
      fetchConnections();
    } catch (err) {
      console.error('Error deleting connection:', err);
      showSnackbar(`Failed to delete connection: ${err.response?.data?.detail || err.message}`, 'error');
    }
  };

  // Open edit dialog
  const handleEdit = (connection) => {
    setFormData({
      name: connection.name || '',
      type: connection.type || 'postgresql',
      host: connection.host || 'localhost',
      port: connection.port || '',
      database: connection.database || '',
      username: connection.username || '',
      password: '', // Don't pre-fill password for security
      options: connection.options ? JSON.stringify(connection.options, null, 2) : '{}',
    });
    setEditingId(connection.id);
    setDialogOpen(true);
  };

  // Open new connection dialog
  const handleNewConnection = () => {
    setFormData({
      name: '',
      type: 'postgresql',
      host: 'localhost',
      port: '',
      database: '',
      username: '',
      password: '',
      options: '{}',
    });
    setEditingId(null);
    setDialogOpen(true);
  };

  // Database types supported by database-operations-mcp
  const databaseTypes = [
    'postgresql',
    'mysql',
    'sqlite',
    'mssql',
    'oracle',
    'sqlalchemy',
    'mongodb',
    'redis',
    'elasticsearch',
    'dynamodb',
  ];

  return (
    <Box sx={{ p: 3 }}>
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          mb: 3,
        }}
      >
        <Typography variant="h6">Database Connections</Typography>
        <Button variant="contained" color="primary" startIcon={<AddIcon />} onClick={handleNewConnection}>
          New Connection
        </Button>
      </Box>

      {/* Connections Table */}
      <TableContainer component={Paper} sx={{ mb: 3 }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Host</TableCell>
              <TableCell>Database</TableCell>
              <TableCell>Status</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={6} align="center">
                  <CircularProgress size={24} />
                </TableCell>
              </TableRow>
            ) : connections.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} align="center">
                  No connections found. Click "New Connection" to add one.
                </TableCell>
              </TableRow>
            ) : (
              connections.map((conn) => (
                <TableRow key={conn.id}>
                  <TableCell>{conn.name}</TableCell>
                  <TableCell>{conn.type}</TableCell>
                  <TableCell>
                    {conn.host}
                    {conn.port ? `:${conn.port}` : ''}
                  </TableCell>
                  <TableCell>{conn.database}</TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      {conn.status === 'connected' ? (
                        <>
                          <CheckCircleIcon color="success" fontSize="small" sx={{ mr: 1 }} />
                          <span>Connected</span>
                        </>
                      ) : (
                        <>
                          <ErrorIcon color="error" fontSize="small" sx={{ mr: 1 }} />
                          <span>Disconnected</span>
                        </>
                      )}
                    </Box>
                  </TableCell>
                  <TableCell align="right">
                    <Tooltip title="Test Connection">
                      <IconButton size="small" onClick={() => testConnection(conn.id)}>
                        <RefreshIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Edit">
                      <IconButton size="small" onClick={() => handleEdit(conn)}>
                        <EditIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete">
                      <IconButton size="small" color="error" onClick={() => deleteConnection(conn.id)}>
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Connection Dialog */}
      <Dialog open={dialogOpen} onClose={() => !saving && setDialogOpen(false)} maxWidth="sm" fullWidth>
        <form onSubmit={handleSubmit}>
          <DialogTitle>{editingId ? 'Edit Connection' : 'New Connection'}</DialogTitle>
          <DialogContent dividers>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Connection Name"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  required
                  margin="normal"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth margin="normal" required>
                  <InputLabel>Database Type</InputLabel>
                  <Select name="type" value={formData.type} onChange={handleChange} label="Database Type">
                    {databaseTypes.map((type) => (
                      <MenuItem key={type} value={type}>
                        {type}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={8}>
                <TextField
                  fullWidth
                  label="Host"
                  name="host"
                  value={formData.host}
                  onChange={handleChange}
                  required
                  margin="normal"
                />
              </Grid>
              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  label="Port"
                  name="port"
                  type="number"
                  value={formData.port}
                  onChange={handleChange}
                  margin="normal"
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Database Name"
                  name="database"
                  value={formData.database}
                  onChange={handleChange}
                  required
                  margin="normal"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Username"
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  margin="normal"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Password"
                  name="password"
                  type="password"
                  value={formData.password}
                  onChange={handleChange}
                  margin="normal"
                  autoComplete="new-password"
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Connection Options (JSON)"
                  name="options"
                  value={formData.options}
                  onChange={handleChange}
                  margin="normal"
                  multiline
                  rows={4}
                  helperText="Additional connection parameters as JSON"
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDialogOpen(false)} disabled={saving}>
              Cancel
            </Button>
            <Button
              type="submit"
              variant="contained"
              color="primary"
              disabled={saving}
              startIcon={saving ? <CircularProgress size={20} /> : null}
            >
              {saving ? 'Saving...' : 'Save Connection'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </Box>
  );
};

export default DatabaseConnectionManager;
