import React, { useState } from 'react';
import { TextField, Button, Typography, Box, CircularProgress } from '@mui/material';
import axios from 'axios';

const ShellToolForm = ({ tool, showSnackbar }) => {
  const [command, setCommand] = useState('');
  const [workingDir, setWorkingDir] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await axios.post('/api/mcp/execute', {
        server: tool.server,
        tool: tool.name,
        params: { 
          command,
          cwd: workingDir || undefined
        }
      });
      setResult(response.data);
      showSnackbar('Command executed successfully', 'success');
    } catch (error) {
      console.error('Error executing command:', error);
      showSnackbar(`Error: ${error.response?.data?.detail || error.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <TextField
        fullWidth
        label="Command"
        value={command}
        onChange={(e) => setCommand(e.target.value)}
        placeholder="e.g., ls -la or dir"
        variant="outlined"
        margin="normal"
        required
      />
      <TextField
        fullWidth
        label="Working Directory (optional)"
        value={workingDir}
        onChange={(e) => setWorkingDir(e.target.value)}
        placeholder="e.g., /path/to/directory"
        variant="outlined"
        margin="normal"
      />
      <Button 
        type="submit" 
        variant="contained" 
        color="primary"
        disabled={loading || !command}
        startIcon={loading ? <CircularProgress size={20} /> : null}
        sx={{ mt: 2 }}
      >
        {loading ? 'Executing...' : 'Run Command'}
      </Button>
      
      {result && (
        <Box mt={2}>
          <Typography variant="subtitle1" gutterBottom>Result:</Typography>
          <Box 
            component="pre" 
            sx={{
              backgroundColor: 'background.paper',
              p: 2,
              borderRadius: 1,
              maxHeight: '400px',
              overflow: 'auto',
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word',
              fontFamily: 'monospace',
              fontSize: '0.875rem',
              border: '1px solid',
              borderColor: 'divider',
            }}
          >
            {typeof result === 'object' ? JSON.stringify(result, null, 2) : String(result)}
          </Box>
        </Box>
      )}
    </form>
  );
};

export default ShellToolForm;
