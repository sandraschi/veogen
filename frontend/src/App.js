import CssBaseline from '@mui/material/CssBaseline';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AnimatePresence } from 'framer-motion';
import React from 'react';
import { Route, BrowserRouter as Router, Routes } from 'react-router-dom';
import { Toaster } from 'sonner';

// Components
import Layout from './components/Layout/Layout';
import VoiceControlSideTab from './components/VoiceControlSideTab';
import MCPDashboard from './components/mcp/MCPDashboard';
import PromptCoachWidget from './components/prompt/PromptCoachWidget.jsx';
import AISearchPage from './pages/AISearchPage';
import AnalyticsPage from './pages/AnalyticsPage';
import AudioStudioPage from './pages/AudioStudioPage';
import BookMakerPage from './pages/BookMakerPage';
import ChatPage from './pages/ChatPage';
import CodeAssistantPage from './pages/CodeAssistantPage';
import ComplianceCenterPage from './pages/ComplianceCenterPage';
import ContentSafetyPage from './pages/ContentSafetyPage';
import DataInsightsPage from './pages/DataInsightsPage';
import DocumentsPage from './pages/DocumentsPage';
import FlowStudioPage from './pages/FlowStudioPage';
import FuturePredictorPage from './pages/FuturePredictorPage';
import GalleryPage from './pages/GalleryPage';
import GeneratePage from './pages/GeneratePage';
import HelpPage from './pages/HelpPage';
import HomePage from './pages/HomePage';
import ImagesPage from './pages/ImagesPage';
import JobsPage from './pages/JobsPage';
import LabPage from './pages/LabPage';
import MovieMakerPage from './pages/MovieMakerPage';
import MultimodalPage from './pages/MultimodalPage';
import MusicPage from './pages/MusicPage';
import SettingsPage from './pages/SettingsPage';
import SoundDesignPage from './pages/SoundDesignPage';
import StyleTransferPage from './pages/StyleTransferPage';
import TranslationPage from './pages/TranslationPage';
import VideoCallDemo from './pages/VideoCallDemo';
import WorkspaceSyncPage from './pages/WorkspaceSyncPage';

import EmailVerification from './components/auth/EmailVerification.jsx';
// Auth Components
import EnhancedAuth from './components/auth/EnhancedAuth.jsx';
import PasswordReset from './components/auth/PasswordReset.jsx';
import ProtectedRoute from './components/auth/ProtectedRoute';
import { AuthProvider } from './contexts/AuthContext';

// Styles
import './App.css';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      refetchOnWindowFocus: false,
    },
  },
});

// Create Material-UI theme
const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#8b5cf6',
    },
    secondary: {
      main: '#ec4899',
    },
    background: {
      default: '#0f0f23',
      paper: '#1a1a2e',
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <AuthProvider>
          <Router>
            <div className="App min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-violet-800">
              <AnimatePresence mode="wait">
                <Routes>
                  {/* Public routes */}
                  <Route path="/auth" element={<EnhancedAuth />} />
                  <Route path="/verify-email" element={<EmailVerification />} />
                  <Route path="/reset-password" element={<PasswordReset />} />
                  <Route path="/mcp" element={<MCPDashboard />} />
                  <Route path="/voice-control" element={<VoiceControlSideTab />} />
                  <Route path="/video-call" element={<VideoCallDemo />} />

                  {/* Dashboard redirect to home */}
                  <Route
                    path="/dashboard"
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <HomePage />
                        </Layout>
                      </ProtectedRoute>
                    }
                  />

                  {/* Protected routes */}
                  <Route
                    path="/"
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <HomePage />
                        </Layout>
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/generate"
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <GeneratePage />
                        </Layout>
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/moviemaker"
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <MovieMakerPage />
                        </Layout>
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/flow"
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <FlowStudioPage />
                        </Layout>
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/bookmaker"
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <BookMakerPage />
                        </Layout>
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/images"
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <ImagesPage />
                        </Layout>
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/music"
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <MusicPage />
                        </Layout>
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/chat"
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <ChatPage />
                        </Layout>
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/search"
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <AISearchPage />
                        </Layout>
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/documents"
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <DocumentsPage />
                        </Layout>
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/code"
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <CodeAssistantPage />
                        </Layout>
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/translation"
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <TranslationPage />
                        </Layout>
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/audio"
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <AudioStudioPage />
                        </Layout>
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/sound-design"
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <SoundDesignPage />
                        </Layout>
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/predictor"
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <FuturePredictorPage />
                        </Layout>
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/analytics"
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <AnalyticsPage />
                        </Layout>
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/safety"
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <ContentSafetyPage />
                        </Layout>
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/compliance"
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <ComplianceCenterPage />
                        </Layout>
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/style"
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <StyleTransferPage />
                        </Layout>
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/insights"
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <DataInsightsPage />
                        </Layout>
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/multimodal"
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <MultimodalPage />
                        </Layout>
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/lab"
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <LabPage />
                        </Layout>
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/gallery"
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <GalleryPage />
                        </Layout>
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/workspace"
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <WorkspaceSyncPage />
                        </Layout>
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/jobs"
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <JobsPage />
                        </Layout>
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/settings"
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <SettingsPage />
                        </Layout>
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/help"
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <HelpPage />
                        </Layout>
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/mcp"
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <MCPDashboard />
                        </Layout>
                      </ProtectedRoute>
                    }
                  />
                </Routes>
              </AnimatePresence>

              {/* Toast notifications */}
              <Toaster position="top-right" theme="dark" richColors closeButton />

              {/* Voice Control Side Tab - Available globally */}
              <VoiceControlSideTab />
              <PromptCoachWidget />
            </div>
          </Router>
        </AuthProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
