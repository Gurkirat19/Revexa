# Revexa security hardening — 2026-10-29

## Implemented
- Session authentication on `/api/review` and `/api/repository/chat`.
- Per-account encrypted GitHub token loaded server-side; repository access verified with GitHub before AI tools run. Global `GITHUB_TOKEN` no longer authorizes user review requests.
- Request-scoped GitHub credentials and per-review repository file cache (no cross-account shared cache).
- Request size checks, IP-based in-process throttling, origin checks on browser mutations, and no-store response headers.
- Production startup validation for HTTPS frontend, secure cookies, and token encryption key.
- Input length validation, GitHub HTTP timeouts, and new offline security regression tests.
- Frontend review/chat fetch requests include session cookies.

## Remaining work before production
1. **GitHub App**: OAuth `repo` scope remains broad for private repository support. Migrate to a GitHub App with fine-grained `Contents: read` and `Pull requests: read` permissions, and add token rotation/revocation.
2. **CSRF**: Origin checks + SameSite=Lax are useful but not a complete CSRF strategy. Add CSRF tokens for state-changing cookie-authenticated routes, including logout and disconnect, before production.
3. **Rate limits**: The current in-memory limits work only in a single worker; use Redis or a reverse proxy for distributed enforcement. Add shared upload-size limits at proxy layer.
4. **Dependencies**: Run `pip-audit` / lock and pin dependency versions in CI; audit browser dependencies and security headers in deployment.
5. **Integration testing**: Run real GitHub OAuth, Google OAuth, private repository authorization, revoked token, and AI-provider tests with test credentials. None were run in this environment.
6. **Secrets**: Rotate any credentials ever committed or shared; ensure production secrets are injected by hosting platform and never logged.
7. **Privacy**: Document third-party AI data transfer, retention/deletion policy, and organization consent for private code.

## Naming conventions
New Python functions use descriptive `snake_case` names, constants use `UPPER_SNAKE_CASE`, and test names use `test_<behavior>`. Existing public JSON fields and API URLs are preserved to avoid breaking frontend compatibility. Legacy modules are left in place to avoid introducing unrelated regressions.

## Run tests
`cd backend && python -m pytest -q tests`
