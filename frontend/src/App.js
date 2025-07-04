import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'sonner';
import { AnimatePresence } from 'framer-motion';

// Components
import Layout from './components/Layout/Layout';
import HomePage from './pages/HomePage';
import GeneratePage from './pages/GeneratePage';
import MovieMakerPage from './pages/MovieMakerPage';
import BookMakerPage from './pages/BookMakerPage';
import ImagesPage from './pages/ImagesPage';
import MusicPage from './pages/MusicPage';
import ChatPage from './pages/ChatPage';
import AISearchPage from './pages/AISearchPage';
import DocumentsPage from './pages/DocumentsPage';
import CodeAssistantPage from './pages/CodeAssistantPage';
import TranslationPage from './pages/TranslationPage';
import AudioStudioPage from './pages/AudioStudioPage';
import FuturePredictorPage from './pages/FuturePredictorPage';
import AnalyticsPage from './pages/AnalyticsPage';
import ContentSafetyPage from './pages/ContentSafetyPage';
import StyleTransferPage from './pages/StyleTransferPage';
import DataInsightsPage from './pages/DataInsightsPage';
import MultimodalPage from './pages/MultimodalPage';
import LabPage from './pages/LabPage';
import GalleryPage from './pages/GalleryPage';
import JobsPage from './pages/JobsPage';
import SettingsPage from './pages/SettingsPage';
import HelpPage from './pages/HelpPage';

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

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="App min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-violet-800">
          <Layout>
            <AnimatePresence mode="wait">
              <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/generate" element={<GeneratePage />} />
                <Route path="/moviemaker" element={<MovieMakerPage />} />
                <Route path="/bookmaker" element={<BookMakerPage />} />
                <Route path="/images" element={<ImagesPage />} />
                <Route path="/music" element={<MusicPage />} />
                <Route path="/chat" element={<ChatPage />} />
                <Route path="/search" element={<AISearchPage />} />
                <Route path="/documents" element={<DocumentsPage />} />
                <Route path="/code" element={<CodeAssistantPage />} />
                <Route path="/translation" element={<TranslationPage />} />
                <Route path="/audio" element={<AudioStudioPage />} />
                <Route path="/predictor" element={<FuturePredictorPage />} />
                <Route path="/analytics" element={<AnalyticsPage />} />
                <Route path="/safety" element={<ContentSafetyPage />} />
                <Route path="/style" element={<StyleTransferPage />} />
                <Route path="/insights" element={<DataInsightsPage />} />
                <Route path="/multimodal" element={<MultimodalPage />} />
                <Route path="/lab" element={<LabPage />} />
                <Route path="/gallery" element={<GalleryPage />} />
                <Route path="/jobs" element={<JobsPage />} />
                <Route path="/settings" element={<SettingsPage />} />
                <Route path="/help" element={<HelpPage />} />
              </Routes>
            </AnimatePresence>
          </Layout>
          
          {/* Toast notifications */}
          <Toaster 
            position="top-right" 
            theme="dark"
            richColors
            closeButton
          />
        </div>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
