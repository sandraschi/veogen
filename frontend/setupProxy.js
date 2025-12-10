const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  // API Proxy
  app.use(
    '/api',
    createProxyMiddleware({
      target: 'http://localhost:8000',
      changeOrigin: true,
      secure: false,
      logLevel: 'debug',
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, PATCH, OPTIONS',
        'Access-Control-Allow-Headers': 'X-Requested-With, content-type, Authorization, X-MCP-Server'
      },
      onProxyReq: (proxyReq) => {
        proxyReq.setHeader('origin', 'http://localhost:3000');
      }
    })
  );

  // MCP Server Proxy
  app.use(
    '/mcp',
    createProxyMiddleware({
      target: 'http://goliath:3000',
      changeOrigin: true,
      secure: false,
      logLevel: 'debug',
      pathRewrite: {
        '^/mcp': '' // Remove /mcp prefix when forwarding
      },
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, PATCH, OPTIONS',
        'Access-Control-Allow-Headers': 'X-Requested-With, content-type, Authorization, X-MCP-Server'
      },
      onProxyReq: (proxyReq) => {
        proxyReq.setHeader('origin', 'http://localhost:3000');
      }
    })
  );
};

// Configure development server
const { createServer } = require('http');
const next = require('next');

const dev = process.env.NODE_ENV !== 'production';
const app = next({ dev });
const handle = app.getRequestHandler();

app.prepare().then(() => {
  createServer((req, res) => {
    const allowedHosts = ['localhost:3000', '127.0.0.1:3000', 'localhost', '127.0.0.1'];
    const host = req.headers.host || '';
    
    if (!allowedHosts.includes(host)) {
      res.statusCode = 403;
      return res.end('Access Denied');
    }
    
    return handle(req, res);
  }).listen(3000, (err) => {
    if (err) throw err;
    console.log('> Ready on http://localhost:3000');
  });
});
