# Revexa AI provider setup

## Gemini

The PR reviewer now reads the Gemini model from `GEMINI_MODEL`. The default is `gemini-3.8-flash`, which replaces the retired `gemini-2.5-flash` model that caused the reported 404.

In `backend/.env`:

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-3.8-flash
```

## Claude

Install backend dependencies, then configure:

```env
ANTHROPIC_API_KEY=your_anthropic_api_key
CLAUDE_MODEL=claude-sonnet-4-5
```

Never commit or share `.env` files. Keep API keys on the backend only.

## Choose a PR review mode

On the Pull Request Review page, select:

- **Gemini** — run the Gemini reviewer.
- **Claude** — run the Claude reviewer.
- **Compare Gemini + Claude** — run both independently and display their findings side by side. If one provider fails, the other provider's result is still shown with the failure message for the unavailable provider.

The compare mode does not silently merge or deduplicate the providers' findings. Review each model's evidence independently before acting on it.

## Install and run (PowerShell)

```powershell
cd G:\revexa_8\backend
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Restart the backend after changing `.env`. The frontend remains served from the `frontend` directory on port 5500.
