"""GitHub OAuth and session endpoints for Code Intelligence.

Set GITHUB_OAUTH_CLIENT_ID, GITHUB_OAUTH_CLIENT_SECRET, APP_SECRET_KEY,
TOKEN_ENCRYPTION_KEY and FRONTEND_URL in backend/.env before enabling OAuth.
"""
import base64
import hashlib
import os
import secrets
import sqlite3
import time
from pathlib import Path
from urllib.parse import urlencode

import requests
from cryptography.fernet import Fernet, InvalidToken
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, EmailStr, Field
from fastapi.responses import RedirectResponse

load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=False)
router = APIRouter(prefix="/api/auth", tags=["authentication"])
DB_PATH = Path(os.getenv("AUTH_DB_PATH", Path(__file__).resolve().parents[1] / "code_intelligence.db"))
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://127.0.0.1:5500").rstrip("/")
CLIENT_ID = os.getenv("GITHUB_OAUTH_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("GITHUB_OAUTH_CLIENT_SECRET", "")
GITHUB_CALLBACK_URL = os.getenv("GITHUB_CALLBACK_URL", "http://127.0.0.1:8000/api/auth/github/callback")
COOKIE_NAME = "ci_session"
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"
APP_ENV = os.getenv("APP_ENV", "development").lower()
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_CALLBACK_URL = os.getenv("GOOGLE_CALLBACK_URL", "http://127.0.0.1:8000/api/auth/google/callback")

class RegisterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)



def _fernet():
    key = os.getenv("TOKEN_ENCRYPTION_KEY", "")
    if not key:
        raise RuntimeError("TOKEN_ENCRYPTION_KEY is not configured")
    try:
        return Fernet(key.encode())
    except Exception as exc:
        raise RuntimeError("TOKEN_ENCRYPTION_KEY must be a valid Fernet key") from exc


def _db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def validate_production_settings():
    if APP_ENV != "production":
        return
    if not COOKIE_SECURE or not FRONTEND_URL.startswith("https://"):
        raise RuntimeError("Production requires COOKIE_SECURE=true and HTTPS FRONTEND_URL")
    if not os.getenv("TOKEN_ENCRYPTION_KEY"):
        raise RuntimeError("Production requires TOKEN_ENCRYPTION_KEY")
    enabled_callbacks = []
    if CLIENT_ID:
        enabled_callbacks.append(GITHUB_CALLBACK_URL)
    if GOOGLE_CLIENT_ID:
        enabled_callbacks.append(GOOGLE_CALLBACK_URL)
    for callback in enabled_callbacks:
        if not callback.startswith("https://"):
            raise RuntimeError("Production OAuth callbacks must use HTTPS")


def require_authenticated_user(request: Request) -> dict:
    user = _current_user(request)
    if user is None:
        raise HTTPException(status_code=401, detail="Sign in to continue")
    return user


def get_user_github_token(user: dict) -> str:
    if not isinstance(user.get("github_id"), int) or user["github_id"] <= 0:
        raise HTTPException(status_code=403, detail="Connect GitHub to access repositories")
    with _db() as database:
        row = database.execute("SELECT github_token FROM users WHERE id=?", (user["id"],)).fetchone()
    if row is None:
        raise HTTPException(status_code=401, detail="Session user no longer exists")
    try:
        token = _fernet().decrypt(row["github_token"].encode()).decode()
    except (InvalidToken, AttributeError):
        raise HTTPException(status_code=503, detail="GitHub credential is unavailable; reconnect GitHub")
    if not token:
        raise HTTPException(status_code=403, detail="Connect GitHub to access repositories")
    return token


def require_repository_access(owner: str, repository: str, token: str) -> None:
    try:
        result = requests.get(
            f"https://api.github.com/repos/{owner}/{repository}",
            headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"},
            timeout=15,
        )
    except requests.RequestException:
        raise HTTPException(status_code=502, detail="Could not verify GitHub repository access")
    if result.status_code in (401, 403, 404):
        raise HTTPException(status_code=403, detail="GitHub repository access was not granted")
    if not result.ok:
        raise HTTPException(status_code=502, detail="GitHub access verification failed")


def init_auth_db():
    validate_production_settings()
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _db() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            github_id INTEGER UNIQUE NOT NULL,
            login TEXT NOT NULL,
            name TEXT,
            email TEXT,
            avatar_url TEXT,
            github_token TEXT NOT NULL,
            created_at INTEGER NOT NULL,
            updated_at INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS sessions (
            session_hash TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            expires_at INTEGER NOT NULL,
            created_at INTEGER NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_sessions_expiry ON sessions(expires_at);
        """)
        # Add authentication-provider columns without disturbing existing GitHub users.
        columns = {row[1] for row in db.execute("PRAGMA table_info(users)").fetchall()}
        if "provider" not in columns:
            db.execute("ALTER TABLE users ADD COLUMN provider TEXT NOT NULL DEFAULT 'github'")
        if "password_hash" not in columns:
            db.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")
        if "google_sub" not in columns:
            db.execute("ALTER TABLE users ADD COLUMN google_sub TEXT")
        db.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_google_sub ON users(google_sub) WHERE google_sub IS NOT NULL")
        # Existing data may contain duplicate emails from different GitHub accounts,
        # so enforce uniqueness only for newly-created password accounts in application logic.


def _hash_session(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()


def _current_user(request: Request):
    raw = request.cookies.get(COOKIE_NAME)
    if not raw:
        return None
    with _db() as db:
        row = db.execute("""SELECT u.id,u.github_id,u.login,u.name,u.email,u.avatar_url,u.provider
            FROM sessions s JOIN users u ON u.id=s.user_id
            WHERE s.session_hash=? AND s.expires_at>?""", (_hash_session(raw), int(time.time()))).fetchone()
    return dict(row) if row else None


def _public_user(user):
    """Return safe session details and a usable provider avatar URL when available."""
    provider = user.get("provider") or "github"
    github_id = user.get("github_id")
    has_github = isinstance(github_id, int) and github_id > 0
    login = user.get("login")
    avatar_url = user.get("avatar_url")
    # Some older rows or provider responses have no stored avatar. GitHub exposes a
    # stable public avatar endpoint by login, so use it as a graceful fallback.
    if not avatar_url and has_github and login:
        from urllib.parse import quote
        avatar_url = f"https://github.com/{quote(str(login), safe='')}.png?size=64"
    # Never expose a non-HTTPS image URL from the session payload.
    if avatar_url and not str(avatar_url).startswith("https://"):
        avatar_url = None
    return {"id": user["id"], "github_id": github_id if has_github else None,
            "login": login, "name": user.get("name"), "email": user.get("email"),
            "avatar_url": avatar_url, "provider": provider,
            "connected": has_github}


def _password_hash(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 310_000)
    return "pbkdf2_sha256$310000$%s$%s" % (base64.urlsafe_b64encode(salt).decode(), base64.urlsafe_b64encode(digest).decode())


def _verify_password(password: str, encoded: str | None) -> bool:
    if not encoded:
        return False
    try:
        algorithm, rounds, salt_text, digest_text = encoded.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        salt = base64.urlsafe_b64decode(salt_text.encode())
        expected = base64.urlsafe_b64decode(digest_text.encode())
        actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, int(rounds))
        return secrets.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def _create_session(response: Response, user_id: int):
    now = int(time.time())
    raw_session = secrets.token_urlsafe(48)
    with _db() as db:
        db.execute("INSERT INTO sessions(session_hash,user_id,expires_at,created_at) VALUES(?,?,?,?)",
                   (_hash_session(raw_session), user_id, now + 60 * 60 * 24 * 7, now))
        db.execute("DELETE FROM sessions WHERE expires_at<=?", (now,))
    response.set_cookie(COOKIE_NAME, raw_session, httponly=True, secure=COOKIE_SECURE,
                        samesite="lax", max_age=60 * 60 * 24 * 7, path="/")


@router.get("/github/login")
def github_login():
    if not CLIENT_ID or not CLIENT_SECRET:
        return RedirectResponse(f"{FRONTEND_URL}/auth.html?auth_error=github_not_configured", status_code=303)
    state = secrets.token_urlsafe(32)
    response = RedirectResponse("https://github.com/login/oauth/authorize?" + urlencode({
        "client_id": CLIENT_ID,
        "redirect_uri": GITHUB_CALLBACK_URL,
        "scope": os.getenv("GITHUB_OAUTH_SCOPES", "read:user user:email repo"),
        "state": state,
    }))
    response.set_cookie("ci_oauth_state", state, httponly=True, secure=COOKIE_SECURE, samesite="lax", max_age=600)
    return response


@router.get("/github/callback")
def github_callback(request: Request, code: str = "", state: str = "", error: str = ""):
    """Complete GitHub OAuth and return actionable errors to the workspace."""
    def redirect_with_error(error_code: str):
        response = RedirectResponse(
            f"{FRONTEND_URL}/auth.html?auth_error={error_code}",
            status_code=303,
        )
        response.delete_cookie("ci_oauth_state", path="/", secure=COOKIE_SECURE, httponly=True, samesite="lax")
        return response

    if error:
        return redirect_with_error("github_denied")

    expected = request.cookies.get("ci_oauth_state")
    if not code or not state or not expected or not secrets.compare_digest(state, expected):
        return redirect_with_error("github_state_invalid")

    if not CLIENT_ID or not CLIENT_SECRET:
        return redirect_with_error("github_not_configured")

    try:
        token_response = requests.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            json={
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "code": code,
                "redirect_uri": GITHUB_CALLBACK_URL,
                "state": state,
            },
            timeout=20,
        )
    except requests.RequestException:
        return redirect_with_error("github_token_exchange_failed")

    if not token_response.ok:
        return redirect_with_error("github_token_exchange_failed")

    token_data = token_response.json()
    access_token = token_data.get("access_token")
    if not access_token:
        # GitHub authorization codes are single-use and expire quickly. A callback
        # refresh/replay commonly arrives here after the first exchange succeeded.
        provider_error = str(token_data.get("error") or "").lower()
        if provider_error in {"bad_verification_code", "incorrect_client_credentials"}:
            return redirect_with_error("github_code_expired")
        return redirect_with_error("github_token_exchange_failed")

    gh_headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    try:
        profile_response = requests.get("https://api.github.com/user", headers=gh_headers, timeout=20)
    except requests.RequestException:
        return redirect_with_error("github_profile_failed")
    if not profile_response.ok:
        return redirect_with_error("github_profile_failed")

    profile = profile_response.json()
    email = profile.get("email")
    if not email:
        try:
            emails = requests.get("https://api.github.com/user/emails", headers=gh_headers, timeout=20)
            if emails.ok:
                email = next((item.get("email") for item in emails.json() if item.get("primary")), None)
        except requests.RequestException:
            pass

    now = int(time.time())
    encrypted_token = _fernet().encrypt(access_token.encode()).decode()
    current = _current_user(request)
    try:
        with _db() as db:
            if current:
                owner = db.execute("SELECT id FROM users WHERE github_id=?", (profile["id"],)).fetchone()
                if owner and owner["id"] != current["id"]:
                    # Never silently merge two Revexa accounts. The user must sign
                    # into the account that already owns this GitHub identity.
                    return redirect_with_error("github_account_conflict")
                db.execute(
                    "UPDATE users SET github_id=?,login=?,avatar_url=COALESCE(?,avatar_url),github_token=?,updated_at=? WHERE id=?",
                    (profile["id"], profile["login"], profile.get("avatar_url"), encrypted_token, now, current["id"]),
                )
                user_id = current["id"]
            else:
                db.execute(
                    """INSERT INTO users(github_id,login,name,email,avatar_url,github_token,created_at,updated_at,provider)
                    VALUES(?,?,?,?,?,?,?,?, 'github')
                    ON CONFLICT(github_id) DO UPDATE SET login=excluded.login,name=excluded.name,
                    email=excluded.email,avatar_url=excluded.avatar_url,github_token=excluded.github_token,
                    provider='github',updated_at=excluded.updated_at""",
                    (profile["id"], profile["login"], profile.get("name"), email, profile.get("avatar_url"),
                     encrypted_token, now, now),
                )
                user = db.execute("SELECT id FROM users WHERE github_id=?", (profile["id"],)).fetchone()
                user_id = user["id"]
    except sqlite3.IntegrityError:
        return redirect_with_error("github_account_conflict")

    response = RedirectResponse(f"{FRONTEND_URL}/app.html?auth=connected", status_code=303)
    _create_session(response, user_id)
    response.delete_cookie("ci_oauth_state", path="/", secure=COOKIE_SECURE, httponly=True, samesite="lax")
    return response


@router.post("/register")
def register_email(payload: RegisterRequest, response: Response):
    email = str(payload.email).strip().lower()
    now = int(time.time())
    with _db() as db:
        existing = db.execute("SELECT id,provider FROM users WHERE lower(email)=? LIMIT 1", (email,)).fetchone()
        if existing:
            raise HTTPException(409, "An account already uses this email. Sign in with its existing provider or use account recovery.")
        # The legacy schema requires GitHub fields. A negative synthetic ID reserves
        # a unique internal identity for non-GitHub accounts; it is never exposed as a GitHub ID.
        synthetic_id = -int(time.time_ns() % 2_000_000_000) - 1
        while db.execute("SELECT 1 FROM users WHERE github_id=?", (synthetic_id,)).fetchone():
            synthetic_id -= 1
        encrypted_empty_token = _fernet().encrypt(b"").decode()
        cursor = db.execute("""INSERT INTO users(github_id,login,name,email,avatar_url,github_token,created_at,updated_at,provider,password_hash)
            VALUES(?,?,?,?,?,?,?,?, 'email', ?)""",
            (synthetic_id, email, payload.name.strip(), email, None, encrypted_empty_token, now, now, _password_hash(payload.password)))
        user_id = cursor.lastrowid
    _create_session(response, user_id)
    return {"ok": True, "message": "Account created", "user": {"name": payload.name.strip(), "email": email, "provider": "email"}}


@router.post("/login")
def login_email(payload: LoginRequest, response: Response):
    email = str(payload.email).strip().lower()
    with _db() as db:
        user = db.execute("SELECT id,password_hash,provider,name,email FROM users WHERE lower(email)=? AND provider='email' LIMIT 1", (email,)).fetchone()
    if not user or not _verify_password(payload.password, user["password_hash"]):
        raise HTTPException(401, "Email or password is incorrect.")
    _create_session(response, user["id"])
    return {"ok": True, "message": "Signed in", "user": {"name": user["name"], "email": user["email"], "provider": "email"}}


@router.get("/google/login")
def google_login():
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        return RedirectResponse(f"{FRONTEND_URL}/auth.html?auth_error=google_not_configured", status_code=303)
    state = secrets.token_urlsafe(32)
    response = RedirectResponse("https://accounts.google.com/o/oauth2/v2/auth?" + urlencode({
        "client_id": GOOGLE_CLIENT_ID, "redirect_uri": GOOGLE_CALLBACK_URL,
        "response_type": "code", "scope": "openid email profile", "state": state,
        "prompt": "select_account"
    }))
    response.set_cookie("ci_google_state", state, httponly=True, secure=COOKIE_SECURE, samesite="lax", max_age=600, path="/")
    return response


@router.get("/google/callback")
def google_callback(request: Request, code: str = "", state: str = "", error: str = ""):
    if error:
        return RedirectResponse(f"{FRONTEND_URL}/auth.html?auth_error=google_denied", status_code=303)
    expected = request.cookies.get("ci_google_state")
    if not code or not state or not expected or not secrets.compare_digest(state, expected):
        raise HTTPException(400, "Invalid or expired Google OAuth state. Please try again.")
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(503, "Google sign-in is not configured")
    token_response = requests.post("https://oauth2.googleapis.com/token", data={
        "code": code, "client_id": GOOGLE_CLIENT_ID, "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_CALLBACK_URL, "grant_type": "authorization_code"
    }, timeout=20)
    if not token_response.ok:
        raise HTTPException(502, "Google authorization could not be completed")
    id_token = token_response.json().get("id_token")
    if not id_token:
        raise HTTPException(401, "Google did not return an identity token")
    # Verify signature, issuer, audience and expiration via Google's maintained library.
    try:
        from google.oauth2 import id_token as google_id_token
        from google.auth.transport import requests as google_requests
        claims = google_id_token.verify_oauth2_token(id_token, google_requests.Request(), GOOGLE_CLIENT_ID)
    except Exception:
        raise HTTPException(401, "Google identity could not be verified")
    if not claims.get("email_verified"):
        raise HTTPException(403, "Use a Google account with a verified email address")
    google_sub = claims.get("sub")
    email = str(claims.get("email", "")).lower()
    if not google_sub or not email:
        raise HTTPException(401, "Google account did not provide a verified identity")
    now = int(time.time())
    with _db() as db:
        user = db.execute("SELECT id,provider FROM users WHERE google_sub=?", (google_sub,)).fetchone()
        if not user:
            existing = db.execute("SELECT id,provider FROM users WHERE lower(email)=? LIMIT 1", (email,)).fetchone()
            if existing:
                # Do not silently link separate login providers based only on matching email.
                return RedirectResponse(f"{FRONTEND_URL}/auth.html?auth_error=account_exists", status_code=303)
            synthetic_id = -int(time.time_ns() % 2_000_000_000) - 1
            while db.execute("SELECT 1 FROM users WHERE github_id=?", (synthetic_id,)).fetchone():
                synthetic_id -= 1
            encrypted_empty_token = _fernet().encrypt(b"").decode()
            cursor = db.execute("""INSERT INTO users(github_id,login,name,email,avatar_url,github_token,created_at,updated_at,provider,google_sub)
                VALUES(?,?,?,?,?,?,?,?, 'google', ?)""",
                (synthetic_id, email, claims.get("name") or email.split("@")[0], email, claims.get("picture"), encrypted_empty_token, now, now, google_sub))
            user_id = cursor.lastrowid
        else:
            user_id = user["id"]
            db.execute("UPDATE users SET name=?,email=?,avatar_url=?,updated_at=? WHERE id=?",
                       (claims.get("name") or email.split("@")[0], email, claims.get("picture"), now, user_id))
    response = RedirectResponse(f"{FRONTEND_URL}/?auth=connected", status_code=303)
    _create_session(response, user_id)
    response.delete_cookie("ci_google_state", path="/")
    return response


@router.get("/me")
def auth_me(request: Request):
    user = _current_user(request)
    return {"authenticated": bool(user), "user": _public_user(user) if user else None}


@router.post("/logout")
def auth_logout(request: Request, response: Response):
    raw = request.cookies.get(COOKIE_NAME)
    if raw:
        with _db() as db:
            db.execute("DELETE FROM sessions WHERE session_hash=?", (_hash_session(raw),))
    response.delete_cookie(COOKIE_NAME, path="/", secure=COOKIE_SECURE, httponly=True, samesite="lax")
    return {"ok": True, "message": "Logged out"}


@router.get("/github/repos")
def github_repositories(request: Request):
    user = _current_user(request)
    if not user:
        raise HTTPException(401, "Sign in to view repositories")
    if not isinstance(user.get("github_id"), int) or user["github_id"] <= 0:
        raise HTTPException(400, "Connect a GitHub account to browse repositories")
    token = get_user_github_token(user)
    result = requests.get("https://api.github.com/user/repos", headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}, params={"sort": "updated", "per_page": 100, "affiliation": "owner,collaborator,organization_member"}, timeout=20)
    if not result.ok:
        raise HTTPException(result.status_code, "GitHub repository request failed. Reconnect GitHub if access has expired.")
    return {"repositories": [{"id": r["id"], "name": r["full_name"], "url": r["html_url"], "private": r["private"], "description": r.get("description"), "default_branch": r.get("default_branch"), "updated_at": r.get("updated_at")} for r in result.json()]}


@router.delete("/github/disconnect")
def github_disconnect(request: Request):
    user = _current_user(request)
    if not user:
        raise HTTPException(401, "Not logged in")
    response = Response(content='{"ok":true}', media_type="application/json")
    if user.get("provider") in {"email", "google"}:
        # Keep the Revexa account intact when unlinking GitHub from a federated account.
        synthetic_id = -int(time.time_ns() % 2_000_000_000) - 1
        with _db() as db:
            while db.execute("SELECT 1 FROM users WHERE github_id=?", (synthetic_id,)).fetchone():
                synthetic_id -= 1
            db.execute("UPDATE users SET github_id=?,login=email,github_token=?,updated_at=? WHERE id=?",
                       (synthetic_id, _fernet().encrypt(b"").decode(), int(time.time()), user["id"]))
    else:
        with _db() as db:
            db.execute("DELETE FROM users WHERE id=?", (user["id"],))
        response.delete_cookie(COOKIE_NAME, path="/")
    return response
