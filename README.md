 HEAD
# Revexa — PR Review & Code Intelligence

Revexa — Every line deserves scrutiny.

Revexa combines GitHub pull-request review with repository question-answering. The frontend is plain HTML/CSS/JavaScript; the API is FastAPI.

## Frontend interaction update

The workspace now includes lightweight motion effects with reduced-motion accessibility support. Repository findings can be expanded, copied, and marked reviewed. The reviewed state is stored in this browser's local storage; it is not yet synchronized to the backend or across browsers. The copy action copies the finding text, not an automatically generated code patch.

## Requirements

- Python 3.10+ (3.11 recommended)
- GitHub account and a GitHub OAuth App
- GitHub personal access token with access to the repositories you want to review
- Gemini API key; Groq key is used by the repository assistant's Groq provider

## 1. Configure environment variables

From the project root, copy `backend/.env.example` to `backend/.env`. Fill in your own values; do not commit or share `backend/.env`.

```powershell
Copy-Item backend/.env.example backend/.env
```

Set `GITHUB_TOKEN`, `GEMINI_API_KEY`, `GROQ_API_KEY`, `GITHUB_OAUTH_CLIENT_ID`, `GITHUB_OAUTH_CLIENT_SECRET`, `GITHUB_CALLBACK_URL`, `FRONTEND_URL`, `TOKEN_ENCRYPTION_KEY`, and `COOKIE_SECURE` in `backend/.env`. Email/password sign-in works with the local account database. For Google sign-in, also configure `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, and `GOOGLE_CALLBACK_URL`.

Create a GitHub OAuth App at https://github.com/settings/developers with:

- Homepage URL: `http://127.0.0.1:5500`
- Authorization callback URL: `http://127.0.0.1:8000/api/auth/github/callback`

Generate the token encryption key with:

```powershell
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Keep this key private and stable. If you change it, previously encrypted GitHub tokens in the local database cannot be decrypted.

For Google OAuth, create a web OAuth client in Google Cloud Console. Add `http://127.0.0.1:5500` as an authorized JavaScript origin and `http://127.0.0.1:8000/api/auth/google/callback` as an authorized redirect URI. Put the client ID and secret in `backend/.env`. Do not place the client secret in frontend files.

## 2. Install backend dependencies

Open PowerShell in the project root:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r backend/requirements.txt
```

If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal, then activate again.

## 3. Start the backend

Open a PowerShell terminal in the project root:

```powershell
cd backend
python -m uvicorn app.main:app --reload
```

API health check: http://127.0.0.1:8000/
API docs: http://127.0.0.1:8000/docs

## 4. Start the frontend

Open a second PowerShell terminal in the project root:

```powershell
cd frontend
python -m http.server 5500
```

Open http://127.0.0.1:5500. Do not open `index.html` directly as a file; use the local HTTP server so cookies, fetch requests, and OAuth redirects behave correctly.

## Automated tests and local checks

Run the offline unit tests from the project root after installing dependencies:

```powershell
$env:PYTHONPATH = "backend"
python -m pytest backend/tests -q
python -m compileall backend/app backend/tests
node --check frontend/app.js
node --check frontend/auth.js
```

The scripts named `backend/manual_*.py` are manual integration probes for the configured GitHub/Gemini/Groq services. They may make network requests and require real credentials, so they are intentionally not collected by `pytest` as automated unit tests.

## Features

- Revexa landing page with a blue-and-charcoal visual system, responsive layout, scroll reveals, and reduced-motion support
- Email/password registration and login using salted PBKDF2 password hashes and server-managed sessions
- Google OAuth sign-in (requires your own Google OAuth client credentials)
- Dedicated animated authentication page with GitHub, Google, and email sign-in options
- GitHub OAuth connect/disconnect flow and authorized repository picker
- Repository assistant using Gemini or Groq
- Pull-request review via `/api/review` with findings, severity, file and line information, and recommendations
- Workspace navigation for dashboard, PR reviews, repository assistant, sessions, activity, analytics, and settings
- Local browser history for recent tasks (not synced across devices)
- Logout redirects back to the public landing page

## Troubleshooting

- **Backend fails at startup:** check that all API keys exist in `backend/.env`; `backend/app/config.py` currently requires GitHub, Gemini, and Groq API keys.
- **GitHub login fails:** verify the OAuth client ID/secret and the exact callback URL.
- **Repository list fails:** reconnect GitHub and verify the OAuth app permissions.
- **PR review fails:** verify `GITHUB_TOKEN` can read the target repository and the Gemini key is valid.
- **Frontend cannot reach API:** keep the backend on port 8000 and frontend on port 5500, and use `127.0.0.1` consistently.

## Security notes

- Do not share or commit `backend/.env`.
- The source ZIP supplied for this update contained real-looking credential values in `.env.example`. Those values have been replaced with placeholders here. Rotate the corresponding GitHub, Gemini, Groq, and OAuth credentials before using the project.
- This is a local-development setup. Before deployment, configure HTTPS, secure cookies, strict CORS origins, secret management, and review token storage and access controls.


## Authentication options

- **Email and password:** Register or sign in from `frontend/auth.html`. Passwords are stored as salted PBKDF2-SHA256 hashes. The app uses the same HTTP-only session cookie for the workspace.
- **GitHub:** Create an OAuth App with the callback URL shown above. GitHub sign-in is also used to retrieve the repositories your account can access.
- **Google:** Set `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, and `GOOGLE_CALLBACK_URL` in `backend/.env`. In Google Cloud Console, set the authorized origin to `http://127.0.0.1:5500` and redirect URI to `http://127.0.0.1:8000/api/auth/google/callback`. Account linking is intentionally not automatic when an email already belongs to another provider.

Email verification and password-reset email delivery are not implemented yet. The UI does not claim that password recovery has been sent.


## Code conventions

- Python modules, functions, variables, and tests use `snake_case`; classes use `PascalCase`; constants use `UPPER_SNAKE_CASE`.
- JavaScript functions and variables use `camelCase`; CSS classes use `kebab-case`.
- Keep API request/response field names stable when refactoring internal identifiers.
- Tests use `test_<behavior_or_expected_result>` and live/manual scripts use the `manual_` prefix so they are not collected by default pytest discovery.

## Production readiness notes

Before a public production launch, configure HTTPS and secure cookies, use a GitHub App with least-privilege repository permissions, deploy a shared rate limiter (for example Redis or an API gateway), complete CSRF and authorization testing, scan dependencies and secrets, and run live OAuth plus Gemini/Groq integration tests. The built-in in-process rate limiter is intended for single-process development and is not a substitute for distributed production rate limiting.


## GitHub OAuth troubleshooting

- `github_account_conflict`: the GitHub identity is already attached to a different Revexa account. Sign out and sign in with the Revexa account that originally connected that GitHub identity. Revexa intentionally does not merge accounts automatically.
- `github_code_expired`: OAuth authorization codes are single-use. Do not refresh or revisit a GitHub callback URL; return to the app and start a new GitHub connection.
- `github_state_invalid`: the short-lived OAuth state cookie is missing or expired. Start a fresh connection in the same browser session.
- `github_token_exchange_failed`: verify `GITHUB_OAUTH_CLIENT_ID`, `GITHUB_OAUTH_CLIENT_SECRET`, and that `GITHUB_CALLBACK_URL` exactly matches the callback URL configured in GitHub OAuth settings.
- For local development, use the same host consistently (`127.0.0.1` rather than mixing it with `localhost`) for `FRONTEND_URL`, browser navigation, and OAuth callback configuration. Cookies are host-scoped.

The callback now redirects to the workspace with a readable status message instead of leaving a raw JSON error page. OAuth authorization codes are single-use; never share callback URLs because they can contain temporary authorization codes.

# Revexa
 origin/main
