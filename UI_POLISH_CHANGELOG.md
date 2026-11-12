# Revexa UI Polish Changelog

## Website header and footer
- Added a compact sticky-header state on scroll.
- Added animated navigation underlines and hover feedback.
- Expanded the landing footer with feature/workflow/sign-in navigation, copyright year, and responsible-use note.
- Added responsive footer layouts for mobile screens.

## Motion and loading states
- Added a secure route-transition overlay for GitHub sign-in and sign-in navigation from the landing page.
- Added a workspace initial-load overlay with a restrained animated progress indicator.
- Added subtle landing hero preview and floating-chip motion, card hover effects, workflow interactions, and anchor arrival feedback.
- Added authentication OAuth redirect loading overlay and preserved the existing submit-button busy state.
- Added reduced-motion overrides for users who request less animation.

## Accessibility and behavior
- Added accessible labels for primary/footer navigation and loading overlays.
- Loading overlays are hidden from assistive technology until active.
- Existing API endpoints, auth flow destinations, and application page structure were preserved.

## Validation performed
- `node --check frontend/auth.js`
- `node --check frontend/app.js`
- Basic HTML structure checks for `index.html`, `app.html`, and `auth.html`
- Local asset reference scan for the three primary pages

These checks do not replace browser-based visual QA or live OAuth/API testing.
