import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  PhotoIcon,
  PlayIcon,
  DownloadIcon,
  HeartIcon,
  ShareIcon,
  FunnelIcon,
  ArrowDownTrayIcon,
} from '@heroicons/react/24/outline';

const GalleryPage = () => {
  const [selectedFilter, setSelectedFilter] = useState('all');
  const [selectedVideo, setSelectedVideo] = useState(null);

  // Mock data - replace with real API call
  const videos = [
    {
      id: 1,
      title: 'Sunset Mountain Vista',
      thumbnail: '/api/placeholder/400/300',
      duration: '5s',
      style: 'cinematic',
      aspectRatio: '16:9',
      createdAt: '2024-01-15',
      likes: 24,
    },
    {
      id: 2,
      title: 'Urban Night Scene',
      thumbnail: '/api/placeholder/400/300',
      duration: '8s',
      style: 'realistic',
      aspectRatio: '16:9',
      createdAt: '2024-01-14',
      likes: 18,
    },
    {
      id: 3,
      title: 'Abstract Art Flow',
      thumbnail: '/api/placeholder/400/300',
      duration: '10s',
      style: 'artistic',
      aspectRatio: '1:1',
      createdAt: '2024-01-13',
      likes: 31,
    },
  ];

  const filters = [
    { id: 'all', name: 'All Videos', count: videos.length },
    { id: 'cinematic', name: 'Cinematic', count: 5 },
    { id: 'realistic', name: 'Realistic', count: 8 },
    { id: 'artistic', name: 'Artistic', count: 3 },
    { id: 'animated', name: 'Animated', count: 2 },
  ];

  const filteredVideos = selectedFilter === 'all' 
    ? videos 
    : videos.filter(video => video.style === selectedFilter);

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center"
      >
        <h1 className="text-3xl md:text-4xl font-bold text-white mb-4">
          Video Gallery
        </h1>
        <p className="text-gray-400">
          Explore amazing videos created with VeoGen AI
        </p>
      </motion.div>

      {/* Filters */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="flex items-center justify-between"
      >
        <div className="flex items-center space-x-1 bg-white/5 backdrop-blur-sm rounded-lg p-1 border border-white/10">
          {filters.map((filter) => (
            <button
              key={filter.id}
              onClick={() => setSelectedFilter(filter.id)}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 ${
                selectedFilter === filter.id
                  ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white'
                  : 'text-gray-400 hover:text-white hover:bg-white/10'
              }`}
            >
              {filter.name}
              <span className="ml-2 text-xs opacity-60">({filter.count})</span>
            </button>
          ))}
        </div>

        <div className="flex items-center space-x-2">
          <button className="flex items-center px-4 py-2 bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg text-gray-400 hover:text-white hover:bg-white/10 transition-colors">
            <FunnelIcon className="w-4 h-4 mr-2" />
            Filter
          </button>
        </div>
      </motion.div>

      {/* Video Grid */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
      >
        {filteredVideos.map((video, index) => (
          <motion.div
            key={video.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="group cursor-pointer"
            onClick={() => setSelectedVideo(video)}
          >
            <div className="bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 overflow-hidden hover:border-white/20 transition-all duration-300 group-hover:scale-105">
              {/* Thumbnail */}
              <div className="relative aspect-video bg-gray-800">
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
                <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                  <div className="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center">
                    <PlayIcon className="w-6 h-6 text-white" />
                  </div>
                </div>
                <div className="absolute top-3 right-3 bg-black/50 backdrop-blur-sm px-2 py-1 rounded text-white text-xs">
                  {video.duration}
                </div>
                <div className="absolute bottom-3 left-3 text-white">
                  <p className="font-medium text-sm">{video.title}</p>
                </div>
              </div>

              {/* Info */}
              <div className="p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs text-gray-400 capitalize">
                    {video.style} • {video.aspectRatio}
                  </span>
                  <span className="text-xs text-gray-400">
                    {new Date(video.createdAt).toLocaleDateString()}
                  </span>
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <button className="flex items-center text-gray-400 hover:text-red-400 transition-colors">
                      <HeartIcon className="w-4 h-4 mr-1" />
                      <span className="text-xs">{video.likes}</span>
                    </button>
                    <button className="text-gray-400 hover:text-white transition-colors">
                      <ShareIcon className="w-4 h-4" />
                    </button>
                  </div>
                  <button className="text-gray-400 hover:text-white transition-colors">
                    <ArrowDownTrayIcon className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </motion.div>

      {filteredVideos.length === 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-12"
        >
          <PhotoIcon className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-white mb-2">No videos found</h3>
          <p className="text-gray-400 mb-6">
            Try adjusting your filters or create your first video
          </p>
          <a
            href="/generate"
            className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-semibold rounded-lg hover:shadow-lg transition-all duration-300"
          >
            Create Video
          </a>
        </motion.div>
      )}
    </div>
  );
};

export default GalleryPage;
