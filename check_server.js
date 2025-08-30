const http = require('http');
const fs = require('fs');

const url = 'http://localhost:5000/';
const logFile = 'server_check.log';

function log(message) {
    const timestamp = new Date().toISOString();
    const logMessage = `[${timestamp}] ${message}\n`;
    console.log(logMessage);
    fs.appendFileSync(logFile, logMessage);
}

log(`Checking if server is running at ${url}`);

const req = http.get(url, (res) => {
    log(`Server responded with status code: ${res.statusCode}`);
    log('Response headers:');
    log(JSON.stringify(res.headers, null, 2));
    
    if (res.statusCode === 200) {
        log('Server is running and accessible!');
    } else {
        log('Server responded but with non-200 status code');
    }
    
    process.exit(0);
});

req.on('error', (error) => {
    log(`Error connecting to server: ${error.message}`);
    log('Make sure the server is running on port 5000');
    process.exit(1);
});

// Set a timeout
setTimeout(() => {
    log('Connection timeout - server might not be running or is not responding');
    req.destroy();
    process.exit(1);
}, 5000);
