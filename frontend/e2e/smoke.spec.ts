import { test, expect } from '@playwright/test';

const BACKEND = 'http://127.0.0.1:11150';

test.describe('Fleet Audit - veogen', () => {
    test('backend health', async ({ request }) => {
        const r = await request.get(`${BACKEND}/health`);
        expect(r.status()).toBe(200);
    });

    test('chat personas API', async ({ request }) => {
        const r = await request.get(`${BACKEND}/api/v1/chat/personas`);
        expect(r.status()).toBe(200);
    });

    test('movie script endpoint registered', async ({ request }) => {
        const r = await request.get(`${BACKEND}/openapi.json`);
        expect(r.status()).toBe(200);
        const spec = await r.json();
        expect(spec.paths['/api/v1/movie/generate-script']).toBeDefined();
    });

    test('diagnostics endpoint (fleet standard)', async ({ request }) => {
        const r = await request.get(`${BACKEND}/api/v1/diagnostics`);
        expect(r.status()).toBe(200);
        const d = await r.json();
        expect(d.status).toBe('ok');
        expect(d.tool_count).toBeGreaterThan(50);
        expect(d.tools.length).toBe(d.tool_count);
        expect(d.system.windows).toBe(true);
    });

    test('mcp surface responds (initialize handshake)', async ({ request }) => {
        const r = await request.post(`${BACKEND}/mcp/`, {
            headers: { Accept: 'application/json, text/event-stream' },
            data: {
                jsonrpc: '2.0',
                id: 1,
                method: 'initialize',
                params: {
                    protocolVersion: '2025-11-25',
                    capabilities: {},
                    clientInfo: { name: 'smoke', version: '1' },
                },
            },
        });
        expect(r.status()).toBe(200);
        const body = await r.text();
        expect(body).toContain('veogen-mcp');
    });

    test('frontend loads without uncaught errors', async ({ page }) => {
        const pageErrors: string[] = [];
        page.on('pageerror', (err) => pageErrors.push(err.message));
        await page.goto('/', { timeout: 15000 });
        await expect(page.locator('#root')).toBeAttached();
        await page.waitForTimeout(2500);
        expect(pageErrors).toEqual([]);
    });

    test('frontend reaches backend via CORS (browser fetch)', async ({ page }) => {
        await page.goto('/');
        await page.waitForTimeout(1500);
        const status = await page.evaluate(async () => {
            const r = await fetch('http://127.0.0.1:11150/api/v1/chat/personas');
            return r.status;
        });
        expect(status).toBe(200);
    });

    test('nav walk: sidebar routes render (authenticated)', async ({ page, request }) => {
        const email = `e2e-${Date.now()}@example.com`;
        const username = `e2euser${Date.now()}`;
        const reg = await request.post(`${BACKEND}/api/v1/enhanced-auth/register`, {
            data: { email, password: 'TestPass123!', username },
        });
        expect([200, 400, 409]).toContain(reg.status());
        const login = await request.post(`${BACKEND}/api/v1/enhanced-auth/login`, {
            data: { email, password: 'TestPass123!' },
        });
        expect(login.status()).toBe(200);
        const { access_token } = await login.json();

        await page.goto('/');
        await page.waitForTimeout(1500);
        await page.evaluate((t) => localStorage.setItem('token', t), access_token);
        await page.goto('/');
        await page.waitForTimeout(2500);

        const links = page.locator('a[href]');
        const count = await links.count();
        expect(count).toBeGreaterThan(5);
        const hrefs = await links.evaluateAll((els) =>
            els.map((el) => (el as HTMLAnchorElement).getAttribute('href')).filter(Boolean),
        );
        for (const href of hrefs.slice(0, 6)) {
            await page.goto(href as string, { timeout: 15000 });
            await expect(page.locator('#root')).toBeAttached();
            await page.waitForTimeout(800);
        }
    });

    test('settings: local + cloud LLM provider panel (authenticated)', async ({ page, request }) => {
        const email = `e2e-llm-${Date.now()}@example.com`;
        await request.post(`${BACKEND}/api/v1/enhanced-auth/register`, {
            data: { email, password: 'TestPass123!', username: `e2ellm${Date.now()}` },
        });
        const login = await request.post(`${BACKEND}/api/v1/enhanced-auth/login`, {
            data: { email, password: 'TestPass123!' },
        });
        const { access_token } = await login.json();

        // writes require login; reads never contain key material
        const anon = await request.post(`${BACKEND}/api/settings/llm`, { data: { provider: 'openai', model: 'x' } });
        expect([401, 403]).toContain(anon.status());

        await page.goto('/');
        await page.evaluate((t) => localStorage.setItem('token', t), access_token);
        await page.goto('/settings');
        await expect(page.getByTestId('llm-providers-panel')).toBeVisible({ timeout: 15000 });
        for (const id of ['ollama', 'lmstudio', 'google', 'openai', 'anthropic']) {
            await expect(page.getByTestId(`llm-provider-card-${id}`)).toBeVisible();
        }
        await expect(page.getByTestId('llm-provider-select')).toBeVisible();
        await expect(page.getByTestId('llm-model-select')).toBeVisible();
        await expect(page.getByTestId('llm-key-google')).toHaveValue('');
    });

    test('movie maker: form + live priced estimate; produce is gated server-side', async ({ page, request }) => {
        const est = await request.post(`${BACKEND}/api/v1/movie/productions/estimate`, {
            data: { title: 'E2E', concept: 'A fox greets the first morning of spring.', scene_count: 4, narration: false },
        });
        expect((await est.json()).total).toBe(1.68);
        const anon = await request.post(`${BACKEND}/api/v1/movie/productions`, {
            data: { title: 'E2E', concept: 'A fox greets the first morning of spring.', produce: true, confirm_cost: true },
        });
        expect([401, 403]).toContain(anon.status());

        const email = `e2e-movie-${Date.now()}@example.com`;
        await request.post(`${BACKEND}/api/v1/enhanced-auth/register`, {
            data: { email, password: 'TestPass123!', username: `e2emovie${Date.now()}` },
        });
        const login = await request.post(`${BACKEND}/api/v1/enhanced-auth/login`, {
            data: { email, password: 'TestPass123!' },
        });
        const { access_token } = await login.json();
        await page.goto('/');
        await page.evaluate((t) => localStorage.setItem('token', t), access_token);
        await page.goto('/moviemaker');
        await expect(page.getByTestId('movie-form')).toBeVisible({ timeout: 15000 });
        await expect(page.getByTestId('movie-estimate')).toContainText('$', { timeout: 10000 });
        const before = await page.getByTestId('movie-estimate').textContent();
        await page.getByRole('combobox').filter({ hasText: 'Lite' }).selectOption('standard');
        await expect(page.getByTestId('movie-estimate')).not.toHaveText(before ?? '', { timeout: 10000 });
        await expect(page.getByTestId('movie-plan')).toBeEnabled();
    });
});
