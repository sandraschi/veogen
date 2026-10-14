import { AnimatePresence, motion } from 'framer-motion';
import React, { useState } from 'react';
import TopBar from '../TopBar';
import Navigation from './Navigation';
import Sidebar from './Sidebar';

const Layout = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 overflow-x-hidden">
      {/* Background Orbs for Depth */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] right-[-10%] w-[500px] h-[500px] bg-purple-600/20 rounded-full blur-[120px]" />
        <div className="absolute bottom-[-10%] left-[-10%] w-[500px] h-[500px] bg-indigo-600/20 rounded-full blur-[120px]" />
      </div>

      {/* Top Bar */}
      <TopBar toggleSidebar={() => setSidebarOpen(!sidebarOpen)} />

      {/* Sidebar - Integrated with Glass Panel */}
      <Sidebar open={sidebarOpen} setOpen={setSidebarOpen} />

      {/* Main content */}
      <div className={`transition-all duration-500 ${sidebarOpen ? 'lg:ml-64' : 'lg:ml-20'} pt-20 pb-16`}>
        <main className="px-4 lg:px-8">
          <AnimatePresence mode="wait">
            <motion.div
              key={window.location.pathname}
              initial={{ opacity: 0, scale: 0.98, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.98, y: -10 }}
              transition={{
                duration: 0.4,
                ease: [0.22, 1, 0.36, 1],
              }}
              className="max-w-7xl mx-auto"
            >
              {children}
            </motion.div>
          </AnimatePresence>
        </main>
      </div>

      {/* Navigation - Bottom bar for mobile, integrated glass */}
      <div className="lg:hidden fixed bottom-0 left-0 right-0 p-4 z-50">
        <div className="glass-panel p-2 flex justify-around items-center h-16">
          <Navigation />
        </div>
      </div>
    </div>
  );
};

export default Layout;
