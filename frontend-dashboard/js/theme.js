/* ==========================================================================
   STREAMFORGE FRONTEND - THEME MANAGER (js/theme.js)
   Handles light & dark mode switching, persistence, system preference detection,
   and dynamic UI element updates.
   ========================================================================== */

class ThemeManager {
  constructor() {
    this.STORAGE_KEY = 'streamforge_theme';
    this.currentTheme = this.getInitialTheme();
    this.init();
  }

  /**
   * Determine initial theme preference from localStorage or OS setting
   */
  getInitialTheme() {
    const savedTheme = localStorage.getItem(this.STORAGE_KEY);
    if (savedTheme === 'light' || savedTheme === 'dark') {
      return savedTheme;
    }
    // Default fallback
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
      return 'light';
    }
    return 'dark';
  }

  init() {
    // Apply theme immediately on load
    this.applyTheme(this.currentTheme);

    // Listen for OS preference changes
    if (window.matchMedia) {
      window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
        if (!localStorage.getItem(this.STORAGE_KEY)) {
          this.setTheme(e.matches ? 'dark' : 'light');
        }
      });
    }

    // Attach event listeners when DOM is ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => this.bindToggleButtons());
    } else {
      this.bindToggleButtons();
    }
  }

  /**
   * Bind event listeners to all theme toggle buttons on the page
   */
  bindToggleButtons() {
    const buttons = document.querySelectorAll('.theme-toggle-btn, #theme-toggle-btn, #login-theme-toggle-btn');
    buttons.forEach(btn => {
      btn.onclick = (e) => {
        if (e) e.preventDefault();
        this.toggleTheme();
      };
      this.updateButtonUI(btn);
    });
  }

  /**
   * Toggle between 'dark' and 'light'
   */
  toggleTheme() {
    const newTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
    this.setTheme(newTheme);
  }

  /**
   * Set theme, update DOM attribute, save preference, and notify subscribers
   * @param {'dark'|'light'} theme 
   */
  setTheme(theme) {
    this.currentTheme = theme;
    localStorage.setItem(this.STORAGE_KEY, theme);
    this.applyTheme(theme);
  }

  /**
   * Apply theme attribute to document and trigger UI & chart updates
   * @param {'dark'|'light'} theme 
   */
  applyTheme(theme) {
    // Set data-theme on html element (safe in <head> and everywhere)
    if (document.documentElement) {
      document.documentElement.setAttribute('data-theme', theme);
    }
    // Set data-theme on body if body is available
    if (document.body) {
      document.body.setAttribute('data-theme', theme);
    }

    // Update all toggle buttons
    const buttons = document.querySelectorAll('.theme-toggle-btn, #theme-toggle-btn, #login-theme-toggle-btn');
    buttons.forEach(btn => this.updateButtonUI(btn));

    // Dispatch global event for components (e.g. ChartController)
    window.dispatchEvent(new CustomEvent('theme:changed', { detail: { theme } }));
  }

  /**
   * Update individual button icon and tooltip
   * @param {HTMLElement} btn 
   */
  updateButtonUI(btn) {
    if (!btn) return;
    const isDark = this.currentTheme === 'dark';
    
    // Update icon if button contains an <i> tag
    const icon = btn.querySelector('i');
    if (icon) {
      icon.className = isDark ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
      icon.style.color = isDark ? '#f59e0b' : '#6366f1';
    }

    // Update button text if it has a label span
    const label = btn.querySelector('.theme-toggle-label');
    if (label) {
      label.textContent = isDark ? 'Light Mode' : 'Dark Mode';
    }

    btn.setAttribute('title', isDark ? 'Switch to Light White Theme' : 'Switch to Dark Obsidian Theme');
    btn.setAttribute('aria-label', isDark ? 'Switch to Light White Theme' : 'Switch to Dark Obsidian Theme');
  }
}

// Instantiate global ThemeManager
window.themeManager = new ThemeManager();
