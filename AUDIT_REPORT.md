# Revexa QA audit — 2026-10-29

## Fixes in this package

- GitHub profile avatar: the `/api/auth/me` session payload now supplies GitHub's public avatar endpoint when a connected GitHub user has no stored avatar URL. The workspace retries that endpoint once if the stored image URL fails and hides the image rather than showing a broken-image icon. Avatar URLs returned to the browser must use HTTPS.
- Backend startup resilience: AI SDK imports are lazy-loaded by provider selection, so an unavailable optional provider SDK does not prevent FastAPI from importing and serving non-AI endpoints. Selecting a provider without its SDK produces a helpful installation error.
- Environment loading: backend `.env` resolution is now anchored to `backend/app/config.py`, rather than depending on the current shell directory.
- Favicon: added `frontend/favicon.svg` and linked it from all three HTML pages, avoiding the browser's missing-favicon request.
- Added offline unit tests for GitHub avatar fallback, HTTPS avatar handling, and non-GitHub accounts.

## Checks performed in the build environment

- `python -m pytest -q backend/tests`: 8 passed.
- `python -m compileall -q backend/app`: passed.
- `node --check` for each `frontend/*.js`: passed.
- Python HTML parser checked local `src`/`href` references in `index.html`, `app.html`, and `auth.html`: no missing local references before adding the favicon; the new favicon file and references were then added.
- FastAPI smoke checks with test environment variables and a temporary SQLite database: `GET /`, `GET /api/auth/me`, `GET /openapi.json`, email registration/session, and logout passed.
- `app.main` imports and registers 13 API paths with dummy environment keys after lazy provider loading.

## Not verified here

- Real GitHub OAuth authorization/token exchange and live avatar network loading (requires the user's configured OAuth app and browser session).
- Real Gemini/Groq requests and real repository/PR review quality (requires valid provider keys and accessible GitHub repositories).
- Browser-based end-to-end UI interactions on the user's machine.

## Run the checks locally

From the project root in PowerShell:

```powershell
$env:PYTHONPATH = "backend"
python -m pytest backend/tests -q
python -m compileall backend/app backend/tests
node --check frontend/app.js
node --check frontend/auth.js
```
