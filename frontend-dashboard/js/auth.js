/* ==========================================================================
   STREAMFORGE FRONTEND - AUTHENTICATION MODULE (js/auth.js)
   ========================================================================== */

class AuthController {
  constructor() {
    this.loginForm = document.getElementById('login-form');
    this.usernameInput = document.getElementById('username');
    this.passwordInput = document.getElementById('password');
    this.usernameError = document.getElementById('username-error');
    this.passwordError = document.getElementById('password-error');
    this.loginView = document.getElementById('login-view');
    this.logoutBtn = document.getElementById('logout-btn');

    this.init();
  }

  init() {
    if (this.loginForm) {
      this.loginForm.addEventListener('submit', (e) => this.handleLogin(e));
    }

    if (this.logoutBtn) {
      this.logoutBtn.addEventListener('click', () => this.handleLogout());
    }

    // Clear error messages on input
    if (this.usernameInput) {
      this.usernameInput.addEventListener('input', () => {
        this.usernameError.textContent = '';
      });
    }
    if (this.passwordInput) {
      this.passwordInput.addEventListener('input', () => {
        this.passwordError.textContent = '';
      });
    }
  }

  /**
   * Validate user input fields
   * @returns {boolean} isValid
   */
  validateForm() {
    let isValid = true;
    const username = this.usernameInput.value.trim();
    const password = this.passwordInput.value.trim();

    if (!username) {
      this.usernameError.textContent = 'Username or Email is required.';
      isValid = false;
    } else if (username.length < 3) {
      this.usernameError.textContent = 'Username must be at least 3 characters.';
      isValid = false;
    } else {
      this.usernameError.textContent = '';
    }

    if (!password) {
      this.passwordError.textContent = 'Password is required.';
      isValid = false;
    } else if (password.length < 6) {
      this.passwordError.textContent = 'Password must be at least 6 characters.';
      isValid = false;
    } else {
      this.passwordError.textContent = '';
    }

    return isValid;
  }

  /**
   * Handle Login Form submission
   */
  async handleLogin(event) {
    event.preventDefault();

    if (!this.validateForm()) {
      return;
    }

    const username = this.usernameInput.value.trim();
    const password = this.passwordInput.value.trim();

    window.Toast.showLoader('Authenticating with StreamForge Backend...');

    try {
      // Attempt login against FastAPI backend API using form-urlencoded format
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);

      const response = await window.apiClient.request('/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData.toString()
      }).catch(async (err) => {
        // Fallback for demo mode if backend is offline or mock creds used
        if ((username === 'admin' || username === 'admin@streamforge.com') && (password === 'password123' || password === 'Admin@12345')) {
          return { access_token: 'mock_jwt_token_streamforge_admin_9921', token_type: 'bearer' };
        }
        throw err;
      });

      // Store JWT token
      if (response && response.access_token) {
        window.apiClient.setToken(response.access_token);
        window.Toast.show('Successfully authenticated! Welcome back, Admin.', 'success');
        this.showDashboard();
      }
    } catch (error) {
      window.Toast.show(error.message || 'Authentication failed. Please check credentials.', 'error');
    } finally {
      window.Toast.hideLoader();
    }
  }

  /**
   * Check if user is currently logged in
   */
  isAuthenticated() {
    return !!window.apiClient.getToken();
  }

  /**
   * Transition view from Login overlay to Dashboard shell
   */
  showDashboard() {
    if (this.loginView) {
      this.loginView.classList.add('hidden');
    }

    // Trigger app shell view setup
    window.dispatchEvent(new Event('auth:success'));
  }

  showLogin() {
    if (this.loginView) {
      this.loginView.classList.remove('hidden');
    }
  }

  /**
   * Handle Logout action
   */
  handleLogout() {
    window.apiClient.removeToken();
    window.Toast.show('Logged out successfully.', 'info');

    this.showLogin();

    window.dispatchEvent(new Event('auth:logout'));
  }
}

// Expose global Auth controller
window.authController = new AuthController();
