import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Bars3Icon,
  BellIcon,
  UserCircleIcon,
  QuestionMarkCircleIcon,
  DocumentTextIcon,
  SunIcon,
  MoonIcon,
  LanguageIcon,
  ChevronDownIcon,
} from '@heroicons/react/24/outline';
import LogViewerModal from '../LogViewerModal';

const TopBar = ({ toggleSidebar, theme, setTheme, language, setLanguage }) => {
  const [showLogViewer, setShowLogViewer] = useState(false);
  const [showLanguageMenu, setShowLanguageMenu] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);

  const languages = [
    { code: 'en', name: 'English', flag: '🇺🇸' },
    { code: 'es', name: 'Español', flag: '🇪🇸' },
    { code: 'fr', name: 'Français', flag: '🇫🇷' },
    { code: 'de', name: 'Deutsch', flag: '🇩🇪' },
    { code: 'ja', name: '日本語', flag: '🇯🇵' },
  ];

  const currentLanguage = languages.find(lang => lang.code === language) || languages[0];

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark');
  };

  const handleHelp = () => {
    window.open('/docs', '_blank');
  };

  return (
    <>
      <header className="bg-white/5 backdrop-blur-xl border-b border-white/10 sticky top-0 z-40">
        <div className="px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Left side */}
            <div className="flex items-center space-x-4">
              <button
                onClick={toggleSidebar}
                className="p-2 rounded-lg text-gray-400 hover:text-white hover:bg-white/10 transition-colors lg:hidden"
              >
                <Bars3Icon className="w-6 h-6" />
              </button>
              
              <div className="hidden lg:flex items-center space-x-3">
                <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-sm">V</span>
                </div>
                <div>
                  <h1 className="text-xl font-bold text-white">VeoGen</h1>
                  <p className="text-xs text-gray-400">AI Video Studio</p>
                </div>
              </div>
            </div>

            {/* Right side */}
            <div className="flex items-center space-x-2">
              {/* Help Button */}
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleHelp}
                className="p-2 text-gray-400 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
                title="Help & Documentation"
              >
                <QuestionMarkCircleIcon className="w-5 h-5" />
              </motion.button>

              {/* Log Viewer Button */}
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setShowLogViewer(true)}
                className="p-2 text-gray-400 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
                title="View System Logs"
              >
                <DocumentTextIcon className="w-5 h-5" />
              </motion.button>

              {/* Theme Toggle */}
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={toggleTheme}
                className="p-2 text-gray-400 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
                title="Toggle Theme"
              >
                {theme === 'dark' ? (
                  <SunIcon className="w-5 h-5" />
                ) : (
                  <MoonIcon className="w-5 h-5" />
                )}
              </motion.button>

              {/* Language Selector */}
              <div className="relative">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setShowLanguageMenu(!showLanguageMenu)}
                  className="flex items-center space-x-2 p-2 text-gray-400 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
                  title="Change Language"
                >
                  <LanguageIcon className="w-5 h-5" />
                  <span className="hidden sm:block text-sm">{currentLanguage.flag}</span>
                  <ChevronDownIcon className="w-4 h-4" />
                </motion.button>

                {showLanguageMenu && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="absolute right-0 mt-2 w-48 bg-gray-900/95 backdrop-blur-xl border border-white/10 rounded-lg shadow-lg overflow-hidden z-50"
                  >
                    {languages.map((lang) => (
                      <button
                        key={lang.code}
                        onClick={() => {
                          setLanguage(lang.code);
                          setShowLanguageMenu(false);
                        }}
                        className={`w-full px-4 py-3 text-left hover:bg-white/10 transition-colors flex items-center space-x-3 ${
                          language === lang.code ? 'bg-white/5 text-white' : 'text-gray-300'
                        }`}
                      >
                        <span className="text-lg">{lang.flag}</span>
                        <span className="text-sm">{lang.name}</span>
                        {language === lang.code && (
                          <div className="ml-auto w-2 h-2 bg-purple-500 rounded-full"></div>
                        )}
                      </button>
                    ))}
                  </motion.div>
                )}
              </div>

              {/* Notifications */}
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="relative p-2 text-gray-400 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
                title="Notifications"
              >
                <BellIcon className="w-5 h-5" />
                <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
              </motion.button>

              {/* User Menu */}
              <div className="relative">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setShowUserMenu(!showUserMenu)}
                  className="flex items-center space-x-3 p-2 text-gray-400 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
                >
                  <UserCircleIcon className="w-6 h-6" />
                  <div className="hidden md:block text-left">
                    <p className="text-sm font-medium text-white">Creator</p>
                    <p className="text-xs text-gray-400">Pro Plan</p>
                  </div>
                  <ChevronDownIcon className="w-4 h-4" />
                </motion.button>

                {showUserMenu && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="absolute right-0 mt-2 w-48 bg-gray-900/95 backdrop-blur-xl border border-white/10 rounded-lg shadow-lg overflow-hidden z-50"
                  >
                    <div className="px-4 py-3 border-b border-white/10">
                      <p className="text-white font-medium">Creator</p>
                      <p className="text-gray-400 text-sm">creator@veogen.com</p>
                    </div>
                    <button className="w-full px-4 py-2 text-left text-gray-300 hover:bg-white/10 hover:text-white transition-colors">
                      Profile Settings
                    </button>
                    <button className="w-full px-4 py-2 text-left text-gray-300 hover:bg-white/10 hover:text-white transition-colors">
                      Billing
                    </button>
                    <button className="w-full px-4 py-2 text-left text-gray-300 hover:bg-white/10 hover:text-white transition-colors">
                      Usage Stats
                    </button>
                    <div className="border-t border-white/10">
                      <button className="w-full px-4 py-2 text-left text-red-400 hover:bg-red-500/10 hover:text-red-300 transition-colors">
                        Sign Out
                      </button>
                    </div>
                  </motion.div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Click outside to close menus */}
        {(showLanguageMenu || showUserMenu) && (
          <div
            className="fixed inset-0 z-30"
            onClick={() => {
              setShowLanguageMenu(false);
              setShowUserMenu(false);
            }}
          />
        )}
      </header>

      {/* Log Viewer Modal */}
      <LogViewerModal
        isOpen={showLogViewer}
        onClose={() => setShowLogViewer(false)}
      />
    </>
  );
};

export default TopBar;
