import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  HomeIcon,
  ChatBubbleBottomCenterTextIcon,
  VideoCameraIcon,
  MusicalNoteIcon,
  PhotoIcon,
  BeakerIcon,
  Cog6ToothIcon,
  QueueListIcon,
  ChevronRightIcon
} from '@heroicons/react/24/outline';

const coreItems = [
  { name: 'Home', href: '/', icon: HomeIcon },
  { name: 'Chat', href: '/chat', icon: ChatBubbleBottomCenterTextIcon },
  { name: 'Video', href: '/generate', icon: VideoCameraIcon },
  { name: 'Music', href: '/music', icon: MusicalNoteIcon },
  { name: 'Images', href: '/images', icon: PhotoIcon },
  { name: 'Gallery', href: '/gallery', icon: QueueListIcon },
];

const labItems = [
  { name: 'Flow Studio', href: '/flow' },
  { name: 'Book Maker', href: '/bookmaker' },
  { name: 'Sound Design', href: '/sound-design' },
  { name: 'AI Search', href: '/search' },
  { name: 'Code Assistant', href: '/code' },
  { name: 'Translation', href: '/translation' },
  { name: 'Future Predictor', href: '/predictor' },
];

const Sidebar = ({ open, setOpen }) => {
  const location = useLocation();
  const [labExpanded, setLabExpanded] = React.useState(false);

  return (
    <>
      {/* Mobile Overlay */}
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm lg:hidden"
            onClick={() => setOpen(false)}
          />
        )}
      </AnimatePresence>

      {/* Desktop Sidebar */}
      <motion.div
        initial={false}
        animate={{ width: open ? 260 : 72 }}
        className="fixed left-0 top-0 z-50 h-screen glass-nav hidden lg:flex flex-col border-r border-white/5"
      >
        {/* Logo Section */}
        <div className="h-20 flex items-center px-6 border-b border-white/5">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500 to-indigo-600 flex items-center justify-center flex-shrink-0 shadow-lg shadow-purple-500/20">
            <span className="text-white font-bold text-xs">V3</span>
          </div>
          {open && (
            <motion.span 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="ml-3 font-bold text-lg premium-gradient"
            >
              VeoGen
            </motion.span>
          )}
        </div>

        {/* Navigation Section */}
        <div className="flex-1 overflow-y-auto overflow-x-hidden py-6 px-3 space-y-2 scrollbar-hide">
          <div className="mb-4">
            <p className={`text-[10px] font-bold text-slate-500 uppercase tracking-widest px-4 mb-2 ${!open && 'text-center'}`}>
              {open ? 'Core Studios' : '•'}
            </p>
            {coreItems.map((item) => {
              const isActive = location.pathname === item.href;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`flex items-center h-12 rounded-xl transition-all duration-300 group ${
                    isActive
                      ? 'bg-purple-600/20 text-purple-300 border border-purple-500/30'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
                  } ${open ? 'px-4 mb-1' : 'justify-center mx-2'}`}
                >
                  <item.icon className={`w-5 h-5 flex-shrink-0 ${isActive && 'text-purple-400'}`} />
                  {open && (
                    <span className="ml-3 text-sm font-medium">{item.name}</span>
                  )}
                  {isActive && open && (
                    <motion.div layoutId="active-pill" className="ml-auto w-1 h-4 bg-purple-500 rounded-full" />
                  )}
                </Link>
              );
            })}
          </div>

          <div>
             <button
              onClick={() => setLabExpanded(!labExpanded)}
              className={`w-full flex items-center h-12 rounded-xl text-slate-400 hover:text-slate-200 hover:bg-white/5 transition-all ${open ? 'px-4' : 'justify-center mx-2'}`}
            >
              <BeakerIcon className="w-5 h-5 flex-shrink-0" />
              {open && (
                <>
                  <span className="ml-3 text-sm font-medium">Experimental</span>
                  <ChevronRightIcon className={`ml-auto w-3 h-3 transition-transform ${labExpanded && 'rotate-90'}`} />
                </>
              )}
            </button>
            
            <AnimatePresence>
              {open && labExpanded && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  className="overflow-hidden bg-white/5 rounded-xl mt-1 mx-2"
                >
                  {labItems.map((item) => (
                    <Link
                      key={item.name}
                      to={item.href}
                      className="flex items-center h-10 px-4 text-xs text-slate-500 hover:text-slate-300 hover:bg-white/5 transition-colors"
                    >
                      {item.name}
                    </Link>
                  ))}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>

        {/* Footer Settings */}
        <div className="p-3 border-t border-white/5">
          <Link
            to="/settings"
            className={`flex items-center h-12 rounded-xl text-slate-400 hover:text-slate-200 hover:bg-white/5 transition-all ${open ? 'px-4' : 'justify-center mx-2'}`}
          >
            <Cog6ToothIcon className="w-5 h-5 flex-shrink-0" />
            {open && <span className="ml-3 text-sm font-medium">Settings</span>}
          </Link>
        </div>
      </motion.div>
    </>
  );
};

export default Sidebar;

