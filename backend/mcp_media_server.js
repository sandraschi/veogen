const express = require('express');
const { VertexAI } = require('@google-cloud/vertexai');

const app = express();
app.use(express.json());

// Initialize Vertex AI
const vertexAI = new VertexAI({
  project: process.env.GCP_PROJECT_ID || 'your-project-id',
  location: 'us-central1',
});

// Initialize models
const veoModel = 'projects/google-cloud-project/locations/us-central1/publishers/google/models/veo-3.0';
const imageGenerationModel = 'imagegeneration@003';
const lyriaModel = 'lyria@003';

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    services: {
      veo: 'available',
      imagen: 'available', 
      lyria: 'available'
    }
  });
});

// Veo 3.0 with Audio Endpoint
app.post('/generate/video', async (req, res) => {
  try {
    const { prompt, duration = 10, resolution = '1080p', style } = req.body;
    
    const videoResponse = await vertexAI.preview.getGenerativeModel({
      model: veoModel,
      generationConfig: {
        temperature: 0.4,
        topK: 32,
        topP: 1,
        maxOutputTokens: 8192,
      },
    }).generateContent({
      contents: [{
        role: 'user',
        parts: [{
          text: prompt,
          videoConfig: {
            duration: `${duration}s`,
            resolution,
            style,
            enableAudio: true, // Enable synchronized audio
          },
        }],
      }],
    });

    res.json({
      success: true,
      videoUrl: videoResponse.videoUri,
      audioUrl: videoResponse.audioUri,
      metadata: videoResponse.metadata
    });
  } catch (error) {
    console.error('Video generation error:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Imagen 3 Image Generation Endpoint
app.post('/generate/image', async (req, res) => {
  try {
    const { prompt, style, resolution = '1024x1024' } = req.body;
    
    const imageResponse = await vertexAI.preview.getGenerativeModel({
      model: imageGenerationModel,
      generationConfig: {
        temperature: 0.4,
        topK: 32,
        topP: 1,
        maxOutputTokens: 8192,
      },
    }).generateContent({
      contents: [{
        role: 'user',
        parts: [{
          text: prompt,
          imageConfig: {
            resolution,
            style,
          },
        }],
      }],
    });

    res.json({
      success: true,
      imageUrl: imageResponse.imageUri,
      metadata: imageResponse.metadata
    });
  } catch (error) {
    console.error('Image generation error:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Lyria Music Generation Endpoint
app.post('/generate/music', async (req, res) => {
  try {
    const { prompt, duration = 30, style } = req.body;
    
    const musicResponse = await vertexAI.preview.getGenerativeModel({
      model: lyriaModel,
      generationConfig: {
        temperature: 0.4,
        topK: 32,
        topP: 1,
        maxOutputTokens: 8192,
      },
    }).generateContent({
      contents: [{
        role: 'user',
        parts: [{
          text: prompt,
          musicConfig: {
            duration: `${duration}s`,
            style,
          },
        }],
      }],
    });

    res.json({
      success: true,
      musicUrl: musicResponse.musicUri,
      metadata: musicResponse.metadata
    });
  } catch (error) {
    console.error('Music generation error:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Text Generation Endpoint
app.post('/generate/text', async (req, res) => {
  try {
    const { prompt, temperature = 0.7, max_tokens = 1000 } = req.body;
    
    const textResponse = await vertexAI.preview.getGenerativeModel({
      model: 'gemini-1.5-pro',
      generationConfig: {
        temperature,
        maxOutputTokens: max_tokens,
      },
    }).generateContent({
      contents: [{
        role: 'user',
        parts: [{ text: prompt }],
      }],
    });

    res.json({
      success: true,
      text: textResponse.text,
      metadata: textResponse.metadata
    });
  } catch (error) {
    console.error('Text generation error:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// List Models Endpoint
app.get('/models', (req, res) => {
  res.json({
    models: [
      'gemini-1.5-pro',
      'gemini-1.5-pro-vision',
      'veo-3',
      'imagen-3',
      'lyria'
    ]
  });
});

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`MCP Media Server running on port ${PORT}`);
  console.log(`Health check: http://localhost:${PORT}/health`);
  console.log(`Video generation: http://localhost:${PORT}/generate/video`);
  console.log(`Image generation: http://localhost:${PORT}/generate/image`);
  console.log(`Music generation: http://localhost:${PORT}/generate/music`);
  console.log(`Text generation: http://localhost:${PORT}/generate/text`);
}); 