# Revexa release-candidate QA report

## Automated checks executed in the build environment
- Backend pytest suite: 16 passed.
- Python compileall: passed.
- Node syntax checks: app.js, auth.js, app1.js, api-config.js passed.
- ZIP integrity: checked after packaging.
- HTML script references: api-config.js is loaded before app.js/auth.js.
- No live third-party OAuth or AI-provider credentials were used.

## Targeted changes in this release
- Added `frontend/api-config.js` so local development uses localhost and production can be pointed to the Render API URL in one place.
- Added `backend/.env.example` with required configuration names and safe blank secret placeholders.
- Added `DEPLOYMENT_CHECKLIST.md` with Vercel/Render configuration, OAuth callback URLs, persistent storage guidance and production limitations.
- Sign-in page no longer silently redirects an already-authenticated user away; it offers Open workspace or Sign out and switch account.
- GitHub OAuth errors return to the sign-in page, where actionable messages can be displayed.
- Kept the supplied project layout, UI, existing backend endpoints and tests.

## Not verified
- Live GitHub OAuth, Google OAuth, Gemini/Groq requests, real PR review, avatar image loading, browser layout, Vercel deployment and Render deployment.
- Dependency vulnerability scan was not run because no dedicated vulnerability scanner was available in this build environment.
- Production security certification is not implied by passing unit tests.

## Before public launch
- Replace the production API placeholder in `frontend/api-config.js`.
- Configure all production secrets in Render, not in frontend files.
- Use a persistent Render disk for the SQLite database.
- Back up `TOKEN_ENCRYPTION_KEY`; changing it invalidates previously encrypted GitHub tokens.
- Use one backend worker until rate limiting is shared across instances.
- Complete live OAuth, AI, private-repository and authorization tests.
