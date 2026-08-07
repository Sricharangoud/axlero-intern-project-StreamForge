/* ==========================================================================
   STREAMFORGE FRONTEND - TOAST & LOADING CONTROLLER (js/toast.js)
   ========================================================================== */

class ToastController {
  constructor() {
    this.container = document.getElementById('toast-container');
    this.loader = document.getElementById('loading-overlay');
    this.loaderText = document.getElementById('loading-text');
  }

  /**
   * Display a dynamic toast notification card
   * @param {string} message - Text message to present
   * @param {string} type - 'success' | 'error' | 'warning' | 'info'
   * @param {number} duration - Auto dismiss delay in ms (default 4000ms)
   */
  show(message, type = 'info', duration = 4000) {
    if (!this.container) return;

    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    // Select icon based on type
    let iconClass = 'fa-circle-info';
    if (type === 'success') iconClass = 'fa-circle-check';
    if (type === 'error') iconClass = 'fa-circle-xmark';
    if (type === 'warning') iconClass = 'fa-triangle-exclamation';

    toast.innerHTML = `
      <div style="display: flex; align-items: center; gap: 10px;">
        <i class="fa-solid ${iconClass}"></i>
        <span style="font-size: 0.85rem; font-weight: 500;">${message}</span>
      </div>
      <button class="toast-close-btn" style="background:none; border:none; color:var(--text-dim); cursor:pointer;">
        <i class="fa-solid fa-xmark"></i>
      </button>
    `;

    // Attach click listener to dismiss button
    const closeBtn = toast.querySelector('.toast-close-btn');
    closeBtn.addEventListener('click', () => {
      this.dismiss(toast);
    });

    // Append to toast container
    this.container.appendChild(toast);

    // Set automatic dismissal timer
    setTimeout(() => {
      this.dismiss(toast);
    }, duration);
  }

  /**
   * Gracefully dismiss and remove toast element from DOM
   */
  dismiss(toast) {
    if (!toast || !toast.parentElement) return;
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => {
      if (toast.parentElement) {
        toast.parentElement.removeChild(toast);
      }
    }, 300);
  }

  /**
   * Show full-screen loading spinner overlay
   * @param {string} message - Optional text label
   */
  showLoader(message = 'Loading data...') {
    if (this.loader) {
      if (this.loaderText) this.loaderText.textContent = message;
      this.loader.classList.remove('hidden');
    }
  }

  /**
   * Hide full-screen loading spinner overlay
   */
  hideLoader() {
    if (this.loader) {
      this.loader.classList.add('hidden');
    }
  }
}

// Expose global Toast controller
window.Toast = new ToastController();
