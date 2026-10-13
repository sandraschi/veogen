import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  // CRA-era process.env.* references (AuthContext, livekit, LogViewerModal)
  // crash in the browser without webpack's DefinePlugin - map them here.
  define: {
    'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV || 'development'),
    'process.env.REACT_APP_API_URL': JSON.stringify('http://localhost:11150'),
    'process.env.REACT_APP_LIVEKIT_WS_URL': JSON.stringify(''),
    'process.env.REACT_APP_LIVEKIT_API_KEY': JSON.stringify(''),
    'process.env.REACT_APP_LIVEKIT_SECRET': JSON.stringify(''),
  },
  // JSX lives in .js files across this codebase (CRA-era) - treat them as JSX
  esbuild: {
    loader: 'jsx',
    include: /\.(js|jsx)$/,
    exclude: [],
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    allowedHosts: ['goliath'],
    port: 11151,
    host: true,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:11150',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
});
