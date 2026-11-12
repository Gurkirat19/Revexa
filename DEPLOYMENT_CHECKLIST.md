# Revexa deployment checklist

## Before pushing to GitHub
1. Keep `.env` files, OAuth secrets, AI keys, databases and token encryption keys out of Git.
2. Rotate any credential that has ever been committed or shared.
3. Push this project to a private GitHub repository while deployment is being tested.
4. Install backend dependencies with `pip install -r backend/requirements.txt`.
5. Run `python -m pytest -q` from `backend/`.

## Frontend API URL
Edit `frontend/api-config.js` and replace:
`https://YOUR-RENDER-SERVICE.onrender.com`
with the actual HTTPS URL assigned to the Render backend. The file uses localhost automatically for local development.

## Render backend
- Root directory: `pr/backend` (if the repository contains the `pr` folder)
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Add a persistent disk and set `AUTH_DB_PATH` to a path on that disk, for example `/var/data/revexa.db`.
- Set `APP_ENV=production`, `COOKIE_SECURE=true`, and `FRONTEND_URL` to the deployed Vercel HTTPS origin.
- Set `TOKEN_ENCRYPTION_KEY` to a generated Fernet key. Back it up securely; changing it makes previously encrypted GitHub tokens unreadable.
- Add GitHub/Google OAuth client credentials and exact HTTPS callback URLs.
- Add at least one AI provider API key.
- Keep only one backend worker until rate limiting is moved to a shared store.

## Vercel frontend
- Set the project root to `pr/frontend` if deploying this folder as the project root.
- Framework preset: Other / static.
- No build command is required for this static frontend.
- Output directory: `.`.
- Update `frontend/api-config.js` with the Render URL before deployment.

## OAuth provider consoles
- GitHub callback: `https://YOUR-RENDER-SERVICE.onrender.com/api/auth/github/callback`
- Google callback: `https://YOUR-RENDER-SERVICE.onrender.com/api/auth/google/callback`
- Use the exact deployed frontend origin in `FRONTEND_URL`.
- OAuth callback URLs must match exactly, including scheme and path.

## Important production limitations to resolve
- Current rate limiting is in-process; do not scale to multiple workers/instances until replaced with Redis or gateway rate limiting.
- Current workspace history uses browser localStorage; it is not shared across browsers/devices and may be cleared by the user.
- Run a dependency vulnerability scan and live OAuth/AI/PR end-to-end tests before public launch.
- Verify CSRF protection and authorization for every state-changing or user-owned resource endpoint.
- Configure privacy/retention disclosures for source code sent to third-party AI providers.
