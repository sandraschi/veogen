import React, { useState } from 'react';
import { 
  TextField, Button, Typography, Box, 
  CircularProgress, Grid, Divider, FormControl, 
  InputLabel, Select, MenuItem, Checkbox, 
  FormControlLabel, TextareaAutosize
} from '@mui/material';
import axios from 'axios';

const EmailToolForm = ({ tool, showSnackbar }) => {
  const [formData, setFormData] = useState({
    to: '',
    cc: '',
    bcc: '',
    subject: '',
    body: '',
    isHtml: false,
    attachments: []
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [attachmentFiles, setAttachmentFiles] = useState([]);

  const handleChange = (e) => {
    const { name, value, checked, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleFileChange = (e) => {
    setAttachmentFiles(Array.from(e.target.files));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      // Prepare form data for file upload
      const formDataToSend = new FormData();
      
      // Add email fields
      formDataToSend.append('to', formData.to);
      formDataToSend.append('subject', formData.subject);
      formDataToSend.append('body', formData.body);
      formDataToSend.append('isHtml', formData.isHtml);
      
      if (formData.cc) formDataToSend.append('cc', formData.cc);
      if (formData.bcc) formDataToSend.append('bcc', formData.bcc);
      
      // Add attachments
      attachmentFiles.forEach((file, index) => {
        formDataToSend.append(`attachments`, file);
      });
      
      const response = await axios.post('/api/mcp/execute', {
        server: tool.server,
        tool: tool.name,
        params: {
          to: formData.to,
          subject: formData.subject,
          body: formData.body,
          is_html: formData.isHtml,
          cc: formData.cc || undefined,
          bcc: formData.bcc || undefined,
          attachments: attachmentFiles.map(file => file.name)
        }
      }, {
        headers: {
          'Content-Type': 'multipart/form-data',
        }
      });
      
      setResult(response.data);
      showSnackbar('Email sent successfully', 'success');
    } catch (error) {
      console.error('Error sending email:', error);
      showSnackbar(`Error: ${error.response?.data?.detail || error.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <TextField
            fullWidth
            label="To"
            name="to"
            value={formData.to}
            onChange={handleChange}
            variant="outlined"
            margin="normal"
            required
          />
        </Grid>
        
        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            label="CC"
            name="cc"
            value={formData.cc}
            onChange={handleChange}
            variant="outlined"
            margin="normal"
          />
        </Grid>
        
        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            label="BCC"
            name="bcc"
            value={formData.bcc}
            onChange={handleChange}
            variant="outlined"
            margin="normal"
          />
        </Grid>
        
        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Subject"
            name="subject"
            value={formData.subject}
            onChange={handleChange}
            variant="outlined"
            margin="normal"
            required
          />
        </Grid>
        
        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Message Body"
            name="body"
            value={formData.body}
            onChange={handleChange}
            variant="outlined"
            margin="normal"
            multiline
            rows={6}
            required
          />
        </Grid>
        
        <Grid item xs={12}>
          <FormControlLabel
            control={
              <Checkbox
                checked={formData.isHtml}
                onChange={handleChange}
                name="isHtml"
                color="primary"
              />
            }
            label="HTML Content"
          />
        </Grid>
        
        <Grid item xs={12}>
          <Button
            variant="outlined"
            component="label"
            sx={{ mt: 1, mb: 2 }}
          >
            Add Attachments
            <input
              type="file"
              hidden
              multiple
              onChange={handleFileChange}
            />
          </Button>
          
          {attachmentFiles.length > 0 && (
            <Box mt={1}>
              <Typography variant="subtitle2">Attachments:</Typography>
              <ul style={{ margin: '4px 0', paddingLeft: '20px' }}>
                {attachmentFiles.map((file, index) => (
                  <li key={index}>{file.name}</li>
                ))}
              </ul>
            </Box>
          )}
        </Grid>
        
        <Grid item xs={12}>
          <Button 
            type="submit" 
            variant="contained" 
            color="primary"
            disabled={loading || !formData.to || !formData.subject || !formData.body}
            startIcon={loading ? <CircularProgress size={20} /> : null}
            sx={{ mt: 1 }}
          >
            {loading ? 'Sending...' : 'Send Email'}
          </Button>
        </Grid>
      </Grid>
      
      {result && (
        <Box mt={3}>
          <Divider sx={{ my: 2 }} />
          <Typography variant="h6">Result:</Typography>
          <pre style={{
            backgroundColor: '#f5f5f5',
            padding: '1rem',
            borderRadius: '4px',
            maxHeight: '300px',
            overflow: 'auto',
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-word'
          }}>
            {JSON.stringify(result, null, 2)}
          </pre>
        </Box>
      )}
    </form>
  );
};

export default EmailToolForm;
