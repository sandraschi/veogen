import React, { useState } from 'react';
import { 
  TextField, Button, Typography, Box, 
  CircularProgress, Grid, Divider, 
  FormControl, InputLabel, Select, MenuItem,
  FormHelperText, Checkbox, FormControlLabel
} from '@mui/material';
import axios from 'axios';

const GenericToolForm = ({ tool, showSnackbar }) => {
  // Generate initial form state from tool parameters
  const [formData, setFormData] = useState(() => {
    const initialData = {};
    if (tool.parameters && typeof tool.parameters === 'object') {
      Object.entries(tool.parameters).forEach(([param, schema]) => {
        if (schema.type === 'boolean') {
          initialData[param] = false;
        } else if (schema.type === 'number') {
          initialData[param] = schema.default || 0;
        } else if (schema.type === 'array') {
          initialData[param] = [];
        } else {
          initialData[param] = schema.default || '';
        }
      });
    }
    return initialData;
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const validateForm = () => {
    const newErrors = {};
    let isValid = true;

    if (tool.parameters) {
      Object.entries(tool.parameters).forEach(([param, schema]) => {
        if (schema.required && !formData[param] && formData[param] !== 0) {
          newErrors[param] = 'This field is required';
          isValid = false;
        } else if (schema.type === 'number' && isNaN(Number(formData[param]))) {
          newErrors[param] = 'Must be a valid number';
          isValid = false;
        }
      });
    }

    setErrors(newErrors);
    return isValid;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      showSnackbar('Please fix the form errors', 'error');
      return;
    }

    setLoading(true);
    
    try {
      // Convert string numbers to actual numbers if needed
      const params = { ...formData };
      if (tool.parameters) {
        Object.entries(tool.parameters).forEach(([param, schema]) => {
          if (schema.type === 'number' && params[param] !== undefined) {
            params[param] = Number(params[param]);
          }
        });
      }

      const response = await axios.post('/api/mcp/execute', {
        server: tool.server,
        tool: tool.name,
        params
      });
      
      setResult(response.data);
      showSnackbar('Operation completed successfully', 'success');
    } catch (error) {
      console.error('Error executing tool:', error);
      showSnackbar(`Error: ${error.response?.data?.detail || error.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  const renderFormField = (param, schema) => {
    const error = errors[param];
    const value = formData[param];
    const label = schema.title || param.replace(/_/g, ' ');
    const description = schema.description || '';
    const isRequired = schema.required === true;

    switch (schema.type) {
      case 'string':
        if (schema.enum) {
          return (
            <FormControl 
              fullWidth 
              margin="normal" 
              error={!!error}
              key={param}
            >
              <InputLabel>{label}{isRequired ? ' *' : ''}</InputLabel>
              <Select
                name={param}
                value={value || ''}
                onChange={handleChange}
                label={`${label}${isRequired ? ' *' : ''}`}
              >
                {schema.enum.map((option) => (
                  <MenuItem key={option} value={option}>
                    {option}
                  </MenuItem>
                ))}
              </Select>
              {description && <FormHelperText>{description}</FormHelperText>}
              {error && <FormHelperText error>{error}</FormHelperText>}
            </FormControl>
          );
        } else if (schema.format === 'multiline' || (schema.maxLength && schema.maxLength > 100)) {
          return (
            <TextField
              key={param}
              fullWidth
              multiline
              rows={4}
              name={param}
              label={`${label}${isRequired ? ' *' : ''}`}
              value={value || ''}
              onChange={handleChange}
              variant="outlined"
              margin="normal"
              error={!!error}
              helperText={error || description}
            />
          );
        } else {
          return (
            <TextField
              key={param}
              fullWidth
              name={param}
              label={`${label}${isRequired ? ' *' : ''}`}
              value={value || ''}
              onChange={handleChange}
              variant="outlined"
              margin="normal"
              error={!!error}
              helperText={error || description}
            />
          );
        }

      case 'number':
        return (
          <TextField
            key={param}
            fullWidth
            type="number"
            name={param}
            label={`${label}${isRequired ? ' *' : ''}`}
            value={value === undefined ? '' : value}
            onChange={handleChange}
            variant="outlined"
            margin="normal"
            error={!!error}
            helperText={error || description}
            inputProps={{
              step: 'any',
              min: schema.minimum,
              max: schema.maximum
            }}
          />
        );

      case 'boolean':
        return (
          <FormControlLabel
            key={param}
            control={
              <Checkbox
                name={param}
                checked={!!value}
                onChange={handleChange}
                color="primary"
              />
            }
            label={
              <Box>
                <Typography>{label}{isRequired ? ' *' : ''}</Typography>
                {description && (
                  <Typography variant="caption" color="textSecondary">
                    {description}
                  </Typography>
                )}
              </Box>
            }
            sx={{ mt: 1, mb: 1, alignItems: 'flex-start' }}
          />
        );

      case 'array':
        return (
          <TextField
            key={param}
            fullWidth
            name={param}
            label={`${label} (comma-separated)${isRequired ? ' *' : ''}`}
            value={Array.isArray(value) ? value.join(', ') : value || ''}
            onChange={(e) => {
              const val = e.target.value;
              const arrayValue = val ? val.split(',').map(item => item.trim()) : [];
              setFormData(prev => ({
                ...prev,
                [param]: arrayValue
              }));
            }}
            variant="outlined"
            margin="normal"
            error={!!error}
            helperText={error || description || 'Separate multiple values with commas'}
          />
        );

      default:
        return (
          <TextField
            key={param}
            fullWidth
            name={param}
            label={`${label}${isRequired ? ' *' : ''}`}
            value={value || ''}
            onChange={handleChange}
            variant="outlined"
            margin="normal"
            error={!!error}
            helperText={error || description}
          />
        );
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <Grid container spacing={2}>
        {tool.parameters ? (
          Object.entries(tool.parameters).map(([param, schema]) => (
            <Grid item xs={12} key={param}>
              {renderFormField(param, schema)}
            </Grid>
          ))
        ) : (
          <Grid item xs={12}>
            <Typography color="textSecondary">
              No parameters required for this tool.
            </Typography>
          </Grid>
        )}
        
        <Grid item xs={12}>
          <Button 
            type="submit" 
            variant="contained" 
            color="primary"
            disabled={loading}
            startIcon={loading ? <CircularProgress size={20} /> : null}
            sx={{ mt: 2 }}
          >
            {loading ? 'Executing...' : 'Execute Tool'}
          </Button>
        </Grid>
      </Grid>
      
      {result && (
        <Box mt={3}>
          <Divider sx={{ my: 2 }} />
          <Typography variant="h6">Result:</Typography>
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

export default GenericToolForm;
