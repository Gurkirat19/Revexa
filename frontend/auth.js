(() => {
  const API_BASE_URL = window.REVEXA_API_BASE_URL || 'http://127.0.0.1:8000';
  const form = document.getElementById('authForm');
  const loginMode = document.getElementById('loginMode');
  const registerMode = document.getElementById('registerMode');
  const nameLabel = document.getElementById('nameLabel');
  const fullName = document.getElementById('fullName');
  const password = document.getElementById('password');
  const togglePassword = document.getElementById('togglePassword');
  const showPasswordCheckbox = document.getElementById('showPasswordCheckbox');
  const loginOptions = document.getElementById('loginOptions');
  const passwordHint = document.getElementById('passwordHint');
  const submitButton = document.getElementById('submitButton');
  const submitText = document.getElementById('submitText');
  const notice = document.getElementById('formNotice');
  const formTitle = document.getElementById('formTitle');
  const formSubtitle = document.getElementById('formSubtitle');
  let mode = 'login';

  document.getElementById('year').textContent = new Date().getFullYear();
  function showNotice(message, isError = false) {
    notice.textContent = message;
    notice.classList.toggle('error', isError);
    notice.hidden = false;
  }
  function clearNotice() { notice.hidden = true; notice.textContent = ''; notice.classList.remove('error'); }
  function setMode(nextMode) {
    mode = nextMode;
    const registering = mode === 'register';
    loginMode.classList.toggle('active', !registering);
    registerMode.classList.toggle('active', registering);
    loginMode.setAttribute('aria-selected', String(!registering));
    registerMode.setAttribute('aria-selected', String(registering));
    nameLabel.classList.toggle('hidden', !registering);
    fullName.required = registering;
    loginOptions.classList.toggle('hidden', registering);
    password.autocomplete = registering ? 'new-password' : 'current-password';
    password.minLength = registering ? 10 : 1;
    passwordHint.textContent = registering ? 'Use at least 10 characters.' : 'Use your account password.';
    formTitle.textContent = registering ? 'Create your account' : 'Welcome back';
    formSubtitle.textContent = registering ? 'Start reviewing code with Revexa.' : 'Sign in to continue to Revexa.';
    submitText.textContent = registering ? 'Create account' : 'Sign in';
    clearNotice();
  }
  loginMode.addEventListener('click', () => setMode('login'));
  registerMode.addEventListener('click', () => setMode('register'));
  function setPasswordVisible(visible) {
    password.type = visible ? 'text' : 'password';
    togglePassword.textContent = visible ? 'Hide' : 'Show';
    togglePassword.setAttribute('aria-label', visible ? 'Hide password' : 'Show password');
    showPasswordCheckbox.checked = visible;
  }
  togglePassword.addEventListener('click', () => setPasswordVisible(password.type === 'password'));
  showPasswordCheckbox.addEventListener('change', () => setPasswordVisible(showPasswordCheckbox.checked));
  function showAuthLoader(){const loader=document.getElementById('authRouteLoader');loader?.classList.add('is-visible');loader?.setAttribute('aria-hidden','false');}
  document.getElementById('githubButton').addEventListener('click', () => { showAuthLoader(); window.location.href = `${API_BASE_URL}/api/auth/github/login`; });
  document.getElementById('googleButton').addEventListener('click', () => { showAuthLoader(); window.location.href = `${API_BASE_URL}/api/auth/google/login`; });
  const query = new URLSearchParams(location.search);
  const authErrorMessages = {
    google_denied: 'Google sign-in was cancelled or denied. You can try again.',
    google_not_configured: 'Google sign-in is not configured yet. Add Google OAuth credentials to backend/.env and try again.',
    github_not_configured: 'GitHub sign-in is not configured yet. Check the OAuth credentials in backend/.env.',
    account_exists: 'An account already uses this email with another sign-in method. Sign in using that original method; accounts are not linked automatically.',
    github_account_conflict: 'This GitHub account is already connected to another Revexa account. Sign out and sign in with the account that originally connected it.',
    github_code_expired: 'The GitHub sign-in code expired or was already used. Please start GitHub sign-in again.',
    github_state_invalid: 'The GitHub sign-in session expired. Please try again.',
    github_token_exchange_failed: 'GitHub could not complete sign-in. Please try again.',
    github_profile_failed: 'Revexa could not retrieve your GitHub profile. Please try again.',
    github_denied: 'GitHub sign-in was cancelled.'
  };
  if (query.get('auth_error')) showNotice(authErrorMessages[query.get('auth_error')] || 'Sign-in could not be completed. Please try again.', true);
  if (query.get('auth') === 'connected') window.location.replace('app.html');

  form.addEventListener('submit', async event => {
    event.preventDefault(); clearNotice();
    const email = document.getElementById('email').value.trim();
    const pass = password.value;
    const name = fullName.value.trim();
    if (!email || !password.checkValidity() || (mode === 'register' && (!name || pass.length < 10))) {
      showNotice(mode === 'register' ? 'Enter your name, a valid email, and a password of at least 10 characters.' : 'Enter a valid email address and password.', true);
      return;
    }
    submitButton.disabled = true;
    submitText.textContent = mode === 'register' ? 'Creating account…' : 'Signing in…';
    try {
      const endpoint = mode === 'register' ? '/api/auth/register' : '/api/auth/login';
      const payload = mode === 'register' ? { name, email, password: pass } : { email, password: pass };
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload)
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.detail || 'Authentication failed. Please try again.');
      showNotice(mode === 'register' ? 'Account created. Opening your workspace…' : 'Signed in. Opening your workspace…');
      showAuthLoader();
      window.setTimeout(() => window.location.replace('app.html'), 350);
    } catch (error) {
      showNotice(error.message || 'The backend could not be reached. Make sure FastAPI is running.', true);
    } finally {
      submitButton.disabled = false;
      submitText.textContent = mode === 'register' ? 'Create account' : 'Sign in';
    }
  });
  fetch(`${API_BASE_URL}/api/auth/me`, { credentials: 'include' }).then(r => r.json()).then(data => {
    if (!data.authenticated) return;
    showNotice('You are already signed in. Continue to your workspace, or sign out to switch accounts.');
    const actions = document.createElement('div');
    actions.className = 'auth-session-actions';
    const continueButton = document.createElement('button');
    continueButton.type = 'button';
    continueButton.className = 'secondary-button';
    continueButton.textContent = 'Open workspace';
    continueButton.addEventListener('click', () => window.location.replace('app.html'));
    const switchButton = document.createElement('button');
    switchButton.type = 'button';
    switchButton.className = 'secondary-button';
    switchButton.textContent = 'Sign out and switch account';
    switchButton.addEventListener('click', async () => {
      switchButton.disabled = true;
      try {
        const response = await fetch(`${API_BASE_URL}/api/auth/logout`, {
          method: 'POST', credentials: 'include'
        });
        if (!response.ok) throw new Error('Could not end the current session.');
        showNotice('You are signed out. You can now sign in with another account.');
        actions.remove();
      } catch (error) {
        showNotice(error.message || 'Could not sign out. Please try again.', true);
        switchButton.disabled = false;
      }
    });
    actions.append(continueButton, switchButton);
    notice.insertAdjacentElement('afterend', actions);
  }).catch(() => {});
})();
