import os
import time
from collections import defaultdict, deque
from threading import Lock
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from app.models import PRRequest,RepositoryChatRequest
from app.auth import (router as auth_router, init_auth_db, FRONTEND_URL,
                      require_authenticated_user, get_user_github_token, require_repository_access)
from app.ai.repository_agent import repository_agent
from app.github.client import (
    parse_pr_url,
    set_request_github_token, reset_request_github_token,
    get_pr,
    get_pr_files,
    parse_repo_url
)
from app.diff.parser import parse_pr_files
from app.agent.risk import calculate_risk
from app.ai.reviewer import review_code
from app.agent.tools import file_cache_context


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_auth_db()
    yield


app = FastAPI(
    title="Revexa API",
    description="AI-powered GitHub repository and pull-request analysis",
    version="1.1.0",
    lifespan=lifespan,
)

app.include_router(auth_router)

# In-process limits protect a single-worker development deployment. For a
# multi-worker production deployment, replace with shared Redis/API-gateway limits.
_request_windows = defaultdict(deque)
_rate_limit_lock = Lock()

@app.middleware("http")
async def security_middleware(request: Request, call_next):
    from fastapi.responses import JSONResponse
    path = request.url.path
    if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        origin = request.headers.get("origin")
        has_session_cookie = bool(request.cookies.get("ci_session"))
        if origin and origin not in _frontend_origins:
            return JSONResponse({"detail": "Untrusted request origin"}, status_code=403)
        # Cookie-authenticated browser mutations must carry a trusted Origin.
        # This is a same-origin/CSRF guard; OAuth callbacks are GET requests.
        if has_session_cookie and not origin:
            return JSONResponse({"detail": "Origin header required for authenticated requests"}, status_code=403)
        if request.headers.get("content-length", "0").isdigit() and int(request.headers.get("content-length", "0")) > 1_048_576:
            return JSONResponse({"detail": "Request too large"}, status_code=413)
    if path in {"/api/review", "/api/repository/chat", "/api/auth/login", "/api/auth/register"}:
        address = request.client.host if request.client else "unknown"
        key = (address, path)
        now = time.monotonic()
        with _rate_limit_lock:
            window = _request_windows[key]
            while window and now - window[0] > 60:
                window.popleft()
            limit = 10 if path.startswith("/api/auth/") else 20
            if len(window) >= limit:
                return JSONResponse({"detail": "Rate limit exceeded"}, status_code=429)
            window.append(now)
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if os.getenv("APP_ENV", "development").lower() == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Cache-Control"] = "no-store" if path.startswith("/api/auth/") else "private, no-store"
    return response


# --------------------------------------------------
# CORS
# --------------------------------------------------

_frontend_origins = list(dict.fromkeys([
    FRONTEND_URL,
    FRONTEND_URL.replace("127.0.0.1", "localhost"),
    "http://localhost:5500",
]))
app.add_middleware(
    CORSMiddleware,
    allow_origins=_frontend_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Health Check
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "PR Review Agent backend is running"
    }


# --------------------------------------------------
# PR Review Endpoint
# --------------------------------------------------

@app.post("/api/review")
def review_pr(request: PRRequest, current_user: dict = Depends(require_authenticated_user)):

    print("Received URL:", repr(request.pr_url))

    try:

        # ------------------------------------------
        # 1. Parse GitHub PR URL
        # ------------------------------------------

        pr_info = parse_pr_url(request.pr_url)
        github_token = get_user_github_token(current_user)
        require_repository_access(pr_info["owner"], pr_info["repo"], github_token)
        token_marker = set_request_github_token(github_token)
        cache_marker = file_cache_context.set({})

        print("Parsed PR:", pr_info)


        # ------------------------------------------
        # 2. Fetch PR information
        # ------------------------------------------

        pr_data = get_pr(
            pr_info["owner"],
            pr_info["repo"],
            pr_info["pr_number"]
        )


        # ------------------------------------------
        # 3. Fetch changed files
        # ------------------------------------------

        pr_files = get_pr_files(
            pr_info["owner"],
            pr_info["repo"],
            pr_info["pr_number"]
        )


        # ------------------------------------------
        # 4. Parse and clean changed files
        # ------------------------------------------

        parsed_files = parse_pr_files(pr_files)

        print(
            "GitHub PR fetched successfully"
        )

        print(
            "Changed files:",
            len(parsed_files)
        )


        # ------------------------------------------
        # 5. Calculate risk
        # ------------------------------------------

        risk = calculate_risk(
            parsed_files
        )

        print(
            "Risk:",
            risk
        )


        # ------------------------------------------
        # 6. Ask Gemini to review the code
        # ------------------------------------------

        review = review_code(
            parsed_files,
            risk,
            request.model
        )

        print(
            "AI review generated successfully"
        )


    except ValueError as error:
        print("ERROR:", error)
        raise HTTPException(status_code=400, detail=str(error))
    except RuntimeError as error:
        # Provider/configuration failures should return a clear API response,
        # rather than an opaque traceback or a misleading successful review.
        print("AI REVIEW ERROR:", error)
        raise HTTPException(status_code=502, detail=str(error))


    finally:
        if "token_marker" in locals():
            reset_request_github_token(token_marker)
            file_cache_context.reset(cache_marker)

    # ----------------------------------------------
    # 7. Return complete PR review
    # ----------------------------------------------

    return {

        "message": "PR reviewed successfully",

        "pr": {

            "title": pr_data["title"],

            "description": pr_data["body"],

            "author": pr_data["user"]["login"],

            "state": pr_data["state"],

            "created_at": pr_data["created_at"],

            "updated_at": pr_data["updated_at"],

            "additions": pr_data["additions"],

            "deletions": pr_data["deletions"],

            "changed_files": pr_data["changed_files"]
        },

        "risk": risk,

        "review": (
    review.model_dump()
    if hasattr(review, "model_dump")
    else review
),

        "files": parsed_files
    }


@app.post("/api/repository/chat")
def repository_chat(
    request: RepositoryChatRequest,
    current_user: dict = Depends(require_authenticated_user)
):

    try:

        repo_info = parse_repo_url(request.repo_url)
        github_token = get_user_github_token(current_user)
        require_repository_access(repo_info["owner"], repo_info["repo"], github_token)
        token_marker = set_request_github_token(github_token)
        cache_marker = file_cache_context.set({})

        result = repository_agent(
            owner=repo_info["owner"],
            repo=repo_info["repo"],
            question=request.question,
            model=request.model
        )
        if result.get("error") or not str(result.get("answer") or "").strip():
            raise HTTPException(
                status_code=502,
                detail=result.get("error") or "The AI provider returned an empty answer. No report was generated."
            )
        return result

    except ValueError as error:

        raise HTTPException(

            status_code=400,

            detail=str(error)
        )
    finally:
        if "token_marker" in locals():
            reset_request_github_token(token_marker)
            file_cache_context.reset(cache_marker)
