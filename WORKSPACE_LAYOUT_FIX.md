# Revexa workspace layout fix

## What changed

- Moved the shared workspace footer inside the main content column. It is no longer a third flex item beside the sidebar and main area.
- Made the main content column flexible (`flex: 1 1 0`, `min-width: 0`) so it fills the remaining viewport width after the sidebar.
- Made the header span the full main content width and kept action/profile controls from forcing horizontal overflow.
- Made the footer sit at the bottom of the main column on tall screens and flow after page content on smaller screens.
- Added tablet/mobile stacking rules so the sidebar, header, page content and footer remain in one responsive flow.
- Kept the existing friendly report presentation, avatar fallback, page loading overlay, and reduced-motion support.

## Files changed

- `frontend/app.html`
- `frontend/style.css`

## Validation

- JavaScript syntax checks: `node --check frontend/app.js` and `node --check frontend/auth.js`.
- HTML parsing: `frontend/index.html`, `frontend/auth.html`, and `frontend/app.html`.
- Structural check: workspace footer is a child of `<main class="main">`.
- Full browser/OAuth/backend integration testing has not been performed in this environment.

## Run locally

Backend:

```powershell
cd backend
python -m uvicorn app.main:app --reload
```

Frontend, in another terminal:

```powershell
cd frontend
python -m http.server 5500
```

Open `http://127.0.0.1:5500`.
