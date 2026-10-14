import {
  Box,
  Button,
  CircularProgress,
  Divider,
  FormControl,
  FormHelperText,
  Grid,
  InputLabel,
  MenuItem,
  Select,
  TextField,
  Typography,
} from '@mui/material';
import axios from 'axios';
import React, { useState } from 'react';

const FileToolForm = ({ tool, showSnackbar }) => {
  const [formData, setFormData] = useState({
    path: '',
    content: '',
    encoding: 'utf-8',
    mode: 'read', // 'read', 'write', 'append', 'delete'
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await axios.post('/api/mcp/execute', {
        server: tool.server,
        tool: tool.name,
        params: {
          ...formData,
          // Only include content if we're writing or appending
          ...(formData.mode !== 'read' && formData.mode !== 'delete' ? { content: formData.content } : {}),
        },
      });

      setResult(response.data);
      showSnackbar(`${tool.name} operation completed successfully`, 'success');
    } catch (error) {
      console.error(`Error in ${tool.name}:`, error);
      showSnackbar(`Error: ${error.response?.data?.detail || error.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Typography variant="h6" gutterBottom>
            {tool.description || tool.name}
          </Typography>
          <Divider sx={{ my: 2 }} />
        </Grid>

        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="File Path"
            name="path"
            value={formData.path}
            onChange={handleChange}
            required
            disabled={loading}
          />
        </Grid>

        <Grid item xs={12} md={6}>
          <FormControl fullWidth disabled={loading}>
            <InputLabel>Operation</InputLabel>
            <Select name="mode" value={formData.mode} label="Operation" onChange={handleChange} required>
              <MenuItem value="read">Read File</MenuItem>
              <MenuItem value="write">Write File</MenuItem>
              <MenuItem value="append">Append to File</MenuItem>
              <MenuItem value="delete">Delete File</MenuItem>
            </Select>
          </FormControl>
        </Grid>

        {(formData.mode === 'write' || formData.mode === 'append') && (
          <Grid item xs={12}>
            <TextField
              fullWidth
              multiline
              rows={6}
              label="File Content"
              name="content"
              value={formData.content}
              onChange={handleChange}
              disabled={loading}
              required={formData.mode === 'write'}
            />
          </Grid>
        )}

        <Grid item xs={12}>
          <Button
            type="submit"
            variant="contained"
            color="primary"
            disabled={loading}
            startIcon={loading ? <CircularProgress size={20} /> : null}
          >
            {loading ? 'Processing...' : 'Execute'}
          </Button>
        </Grid>

        {result && (
          <Grid item xs={12}>
            <Box sx={{ mt: 2, p: 2, bgcolor: 'background.paper', borderRadius: 1 }}>
              <Typography variant="subtitle2" gutterBottom>
                Result:
              </Typography>
              <pre
                style={{
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                  margin: 0,
                  fontFamily: 'monospace',
                  fontSize: '0.875rem',
                  maxHeight: '300px',
                  overflow: 'auto',
                  padding: '8px',
                  backgroundColor: 'rgba(0, 0, 0, 0.1)',
                  borderRadius: '4px',
                }}
              >
                {typeof result === 'object' ? JSON.stringify(result, null, 2) : String(result)}
              </pre>
            </Box>
          </Grid>
        )}
      </Grid>
    </Box>
  );
};

export default FileToolForm;
