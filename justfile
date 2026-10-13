# VeoGen Industrial - salvage phase recipes
# Ports: backend 11150, frontend 11151 (registered in WEBAPP_PORTS.md)

serve:  # start backend (uvicorn, hot reload)
    Set-Location backend; uv run uvicorn app.main:app --host 127.0.0.1 --port 11150 --reload

dev:  # start frontend (vite dev server)
    Set-Location frontend; npm run dev

test:  # backend tests
    Set-Location backend; uv run pytest -q

lint:  # ruff check
    Set-Location backend; uv run ruff check app/

start:  # full stack launcher
    pwsh -NoProfile -File start.ps1

e2e:  # Playwright smoke (backend + frontend, headless)
    Set-Location frontend; bunx playwright test
