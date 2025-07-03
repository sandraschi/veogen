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
import GalleryPage from './pages/GalleryPage';
import JobsPage from './pages/JobsPage';
import SettingsPage from './pages/SettingsPage';

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
                <Route path="/gallery" element={<GalleryPage />} />
                <Route path="/jobs" element={<JobsPage />} />
                <Route path="/settings" element={<SettingsPage />} />
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
