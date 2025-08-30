const path = require('path');

module.exports = {
  devServer: {
    allowedHosts: 'all',
    host: '127.0.0.1',
    port: 3000,
    client: {
      webSocketURL: 'ws://127.0.0.1:3000/ws',
      overlay: {
        errors: true,
        warnings: false,
      },
    },
    hot: true,
    open: true,
    historyApiFallback: true,
    static: {
      directory: path.join(__dirname, 'public'),
    },
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
  webpack: {
    configure: {
      resolve: {
        fallback: {
          fs: false,
          path: false,
          os: false,
        },
      },
    },
  },
};
