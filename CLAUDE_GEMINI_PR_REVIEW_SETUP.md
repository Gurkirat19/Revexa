# Revexa PR review: Gemini + Claude

## Configure backend/.env (keep this file private)
Set:
```env
GEMINI_API_KEY=your_gemini_key
GEMINI_MODEL=gemini-3.8-flash
ANTHROPIC_API_KEY=your_anthropic_key
CLAUDE_MODEL=claude-sonnet-4-5
```
Remove or update any older `GEMINI_MODEL=gemini-2.5-flash` value. The backend loads `backend/.env`; restart Uvicorn after editing it.

## Install and run (PowerShell)
```powershell
cd G:\revexa_8\backend
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

In Revexa, open PR Reviews, paste the GitHub PR URL, choose Gemini, Claude, or Compare Gemini + Claude, then run the review.

Compare mode sends the same diff to both providers. If one provider fails, the successful provider's review is returned with the other provider's error. If both fail, the API returns an error rather than a successful/empty review.

This package deliberately excludes `.env`, local databases, virtual environments, and Python cache files. Preserve your existing `backend/.env` locally and update its values; never share API keys.
