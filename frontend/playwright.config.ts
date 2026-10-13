import { defineConfig } from '@playwright/test';

const BACKEND = 'http://127.0.0.1:11150';
const FRONTEND = 'http://127.0.0.1:11151';

export default defineConfig({
    testDir: './e2e',
    timeout: 60000,
    retries: 1,
    use: {
        baseURL: FRONTEND,
        headless: true,
        screenshot: 'only-on-failure',
    },
    webServer: [
        {
            command: 'uv run uvicorn app.main:app --host 127.0.0.1 --port 11150 --log-level warning',
            url: `${BACKEND}/health`,
            cwd: '../backend',
            reuseExistingServer: false,
            timeout: 60000,
        },
        {
            command: 'bun run dev',
            url: FRONTEND,
            cwd: '.',
            reuseExistingServer: false,
            timeout: 60000,
        },
    ],
});
