import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  XMarkIcon,
  DocumentTextIcon,
  FunnelIcon,
  MagnifyingGlassIcon,
  ArrowDownTrayIcon,
  PlayIcon,
  PauseIcon,
} from '@heroicons/react/24/outline';

const LogViewerModal = ({ isOpen, onClose }) => {
  const [logs, setLogs] = useState([]);
  const [filteredLogs, setFilteredLogs] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedLevel, setSelectedLevel] = useState('all');
  const [selectedComponent, setSelectedComponent] = useState('all');
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(2000);
  
  const logContainerRef = useRef(null);
  const intervalRef = useRef(null);

  const logLevels = ['all', 'debug', 'info', 'warning', 'error'];
  const components = ['all', 'backend', 'frontend', 'database', 'redis', 'gemini', 'ffmpeg'];

  // Mock log data - replace with real API call
  const mockLogs = [
    {
      id: 1,
      timestamp: new Date().toISOString(),
      level: 'info',
      component: 'backend',
      message: 'Video generation started for job abc123',
      details: { jobId: 'abc123', userId: 'user456' }
    },
    {
      id: 2,
      timestamp: new Date(Date.now() - 5000).toISOString(),
      level: 'debug',
      component: 'gemini',
      message: 'Gemini CLI response received',
      details: { responseTime: '2.3s', tokens: 150 }
    },
    {
      id: 3,
      timestamp: new Date(Date.now() - 10000).toISOString(),
      level: 'warning',
      component: 'redis',
      message: 'Redis connection timeout, retrying...',
      details: { attempt: 2, maxRetries: 3 }
    },
    {
      id: 4,
      timestamp: new Date(Date.now() - 15000).toISOString(),
      level: 'error',
      component: 'ffmpeg',
      message: 'Failed to extract frame from video',
      details: { error: 'Invalid video format', file: 'temp_video.mp4' }
    },
    {
      id: 5,
      timestamp: new Date(Date.now() - 20000).toISOString(),
      level: 'info',
      component: 'database',
      message: 'Database connection established',
      details: { connectionPool: 5, activeConnections: 2 }
    },
  ];

  useEffect(() => {
    if (isOpen) {
      setLogs(mockLogs);
      if (autoRefresh) {
        startAutoRefresh();
      }
    } else {
      stopAutoRefresh();
    }
    return () => stopAutoRefresh();
  }, [isOpen, autoRefresh, refreshInterval]);

  useEffect(() => {
    filterLogs();
  }, [logs, searchTerm, selectedLevel, selectedComponent]);

  useEffect(() => {
    if (logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [filteredLogs]);

  const startAutoRefresh = () => {
    stopAutoRefresh();
    intervalRef.current = setInterval(() => {
      fetchLogs();
    }, refreshInterval);
  };

  const stopAutoRefresh = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  };

  const fetchLogs = async () => {
    try {
      const newLog = {
        id: Date.now(),
        timestamp: new Date().toISOString(),
        level: ['info', 'debug', 'warning'][Math.floor(Math.random() * 3)],
        component: components[Math.floor(Math.random() * (components.length - 1)) + 1],
        message: `System activity at ${new Date().toLocaleTimeString()}`,
        details: { processId: Math.floor(Math.random() * 10000) }
      };
      
      setLogs(prevLogs => [...prevLogs, newLog].slice(-1000));
    } catch (error) {
      console.error('Failed to fetch logs:', error);
    }
  };

  const filterLogs = () => {
    let filtered = [...logs];

    if (selectedLevel !== 'all') {
      filtered = filtered.filter(log => log.level === selectedLevel);
    }

    if (selectedComponent !== 'all') {
      filtered = filtered.filter(log => log.component === selectedComponent);
    }

    if (searchTerm) {
      filtered = filtered.filter(log =>
        log.message.toLowerCase().includes(searchTerm.toLowerCase()) ||
        log.component.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    setFilteredLogs(filtered);
  };

  const getLevelColor = (level) => {
    switch (level) {
      case 'error': return 'text-red-400 bg-red-500/10';
      case 'warning': return 'text-yellow-400 bg-yellow-500/10';
      case 'info': return 'text-blue-400 bg-blue-500/10';
      case 'debug': return 'text-gray-400 bg-gray-500/10';
      default: return 'text-gray-400 bg-gray-500/10';
    }
  };

  const exportLogs = () => {
    const logData = filteredLogs.map(log => ({
      timestamp: log.timestamp,
      level: log.level,
      component: log.component,
      message: log.message,
      details: log.details
    }));

    const blob = new Blob([JSON.stringify(logData, null, 2)], {
      type: 'application/json'
    });

    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `veogen-logs-${new Date().toISOString().slice(0, 10)}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 bg-black/80 backdrop-blur-sm"
            onClick={onClose}
          />

          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            className="relative bg-gray-900/95 backdrop-blur-xl border border-white/10 rounded-2xl w-full max-w-6xl h-[80vh] flex flex-col"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-white/10">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-500 rounded-lg flex items-center justify-center">
                  <DocumentTextIcon className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-white">System Logs</h2>
                  <p className="text-gray-400 text-sm">Real-time system activity</p>
                </div>
              </div>

              <button
                onClick={onClose}
                className="p-2 text-gray-400 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
              >
                <XMarkIcon className="w-6 h-6" />
              </button>
            </div>

            {/* Controls */}
            <div className="p-4 border-b border-white/10 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  {/* Search */}
                  <div className="relative">
                    <MagnifyingGlassIcon className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                    <input
                      type="text"
                      placeholder="Search logs..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10 pr-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 w-64"
                    />
                  </div>

                  {/* Level Filter */}
                  <select
                    value={selectedLevel}
                    onChange={(e) => setSelectedLevel(e.target.value)}
                    className="px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                  >
                    {logLevels.map(level => (
                      <option key={level} value={level} className="bg-gray-800">
                        {level.charAt(0).toUpperCase() + level.slice(1)}
                      </option>
                    ))}
                  </select>

                  {/* Component Filter */}
                  <select
                    value={selectedComponent}
                    onChange={(e) => setSelectedComponent(e.target.value)}
                    className="px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                  >
                    {components.map(component => (
                      <option key={component} value={component} className="bg-gray-800">
                        {component.charAt(0).toUpperCase() + component.slice(1)}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="flex items-center space-x-2">
                  {/* Auto Refresh Toggle */}
                  <button
                    onClick={() => setAutoRefresh(!autoRefresh)}
                    className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors ${
                      autoRefresh
                        ? 'bg-green-500/20 text-green-400'
                        : 'bg-white/10 text-gray-400 hover:text-white'
                    }`}
                  >
                    {autoRefresh ? <PauseIcon className="w-4 h-4" /> : <PlayIcon className="w-4 h-4" />}
                    <span className="text-sm">{autoRefresh ? 'Pause' : 'Start'}</span>
                  </button>

                  {/* Export Button */}
                  <button
                    onClick={exportLogs}
                    className="flex items-center space-x-2 px-3 py-2 bg-white/10 hover:bg-white/20 text-gray-400 hover:text-white rounded-lg transition-colors"
                  >
                    <ArrowDownTrayIcon className="w-4 h-4" />
                    <span className="text-sm">Export</span>
                  </button>
                </div>
              </div>

              {/* Stats */}
              <div className="flex items-center space-x-6 text-sm text-gray-400">
                <span>Total: {logs.length}</span>
                <span>Filtered: {filteredLogs.length}</span>
                <span>Auto-refresh: {autoRefresh ? `${refreshInterval/1000}s` : 'Off'}</span>
              </div>
            </div>

            {/* Log Content */}
            <div
              ref={logContainerRef}
              className="flex-1 overflow-y-auto p-4 space-y-2 font-mono text-sm"
            >
              {filteredLogs.map((log) => (
                <motion.div
                  key={log.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="bg-white/5 backdrop-blur-sm rounded-lg p-3 border border-white/10 hover:border-white/20 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-3 flex-1">
                      <span className="text-gray-500 text-xs">
                        {new Date(log.timestamp).toLocaleTimeString()}
                      </span>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getLevelColor(log.level)}`}>
                        {log.level.toUpperCase()}
                      </span>
                      <span className="px-2 py-1 bg-gray-500/20 text-gray-300 rounded text-xs">
                        {log.component}
                      </span>
                    </div>
                  </div>
                  <div className="mt-2 text-gray-200">
                    {log.message}
                  </div>
                  {log.details && (
                    <details className="mt-2">
                      <summary className="text-gray-400 text-xs cursor-pointer hover:text-white">
                        Details
                      </summary>
                      <pre className="text-gray-400 text-xs mt-1 bg-black/20 p-2 rounded overflow-x-auto">
                        {JSON.stringify(log.details, null, 2)}
                      </pre>
                    </details>
                  )}
                </motion.div>
              ))}

              {filteredLogs.length === 0 && (
                <div className="text-center py-12">
                  <DocumentTextIcon className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-white mb-2">No logs found</h3>
                  <p className="text-gray-400">
                    Try adjusting your filters or search terms
                  </p>
                </div>
              )}
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
};

export default LogViewerModal;
