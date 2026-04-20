import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  HomeIcon,
  ChatBubbleBottomCenterTextIcon,
  VideoCameraIcon,
  MusicalNoteIcon,
  PhotoIcon,
  BeakerIcon,
  Cog6ToothIcon,
  QueueListIcon
} from '@heroicons/react/24/outline';

const navigationItems = [
  { name: 'Home', href: '/', icon: HomeIcon },
  { name: 'Chat', href: '/chat', icon: ChatBubbleBottomCenterTextIcon },
  { name: 'Video', href: '/generate', icon: VideoCameraIcon },
  { name: 'Music', href: '/music', icon: MusicalNoteIcon },
  { name: 'Images', href: '/images', icon: PhotoIcon },
  { name: 'Gallery', href: '/gallery', icon: QueueListIcon },
  { name: 'Lab', href: '/lab', icon: BeakerIcon },
  { name: 'Settings', href: '/settings', icon: Cog6ToothIcon },
];

const Navigation = () => {
  const location = useLocation();

  return (
    <div className="flex items-center justify-around w-full gap-2 px-2">
      {navigationItems.map((item) => {
        const isActive = location.pathname === item.href;
        return (
          <Link
            key={item.name}
            to={item.href}
            className="group flex flex-col items-center flex-1 py-1"
          >
            <motion.div
              whileHover={{ y: -2 }}
              whileTap={{ scale: 0.9 }}
              className={`p-2 rounded-xl transition-all duration-300 ${
                isActive
                  ? 'bg-purple-600 text-white shadow-[0_0_15px_rgba(168,85,247,0.4)]'
                  : 'text-slate-400 group-hover:text-slate-200 group-hover:bg-white/5'
              }`}
            >
              <item.icon className="w-5 h-5" />
            </motion.div>
            <span
              className={`text-[10px] mt-1 transition-colors duration-300 ${
                isActive ? 'text-white font-medium' : 'text-slate-500'
              }`}
            >
              {item.name}
            </span>
          </Link>
        );
      })}
    </div>
  );
};

export default Navigation;
鼓
