/* ==========================================================================
   STREAMFORGE FRONTEND - MAIN APPLICATION ROUTER & TICKER (js/app.js)
   ========================================================================== */

class Application {
  constructor() {
    this.sidebar = document.getElementById('app-sidebar');
    this.navbar = document.getElementById('app-header');
    this.mainContent = document.getElementById('main-content');
    this.toggleSidebarBtn = document.getElementById('toggle-sidebar-btn');
    this.navItems = document.querySelectorAll('.nav-item');
    this.viewSections = document.querySelectorAll('.view-section');
    this.clockElem = document.getElementById('live-clock');

    this.activeView = 'dashboard';
    this.pollingInterval = null;

    this.init();
  }

  init() {
    // Register global authentication event listeners
    window.addEventListener('auth:success', () => this.handleAuthenticated());
    window.addEventListener('auth:logout', () => this.handleLoggedOut());
    window.addEventListener('auth:unauthorized', () => this.handleLoggedOut());

    // Toggle Sidebar collapse
    if (this.toggleSidebarBtn) {
      this.toggleSidebarBtn.addEventListener('click', () => this.toggleSidebar());
    }

    // Sidebar navigation link clicks
    this.navItems.forEach(item => {
      item.addEventListener('click', (e) => {
        e.preventDefault();
        const targetView = item.getAttribute('data-view');
        this.switchView(targetView);
      });
    });

    // Start Live Clock
    this.startClock();

    // Check existing authentication state on load
    if (window.authController.isAuthenticated()) {
      window.authController.showDashboard();
    } else {
      window.authController.showLogin();
    }
  }

  /**
   * Handle UI state after successful authentication
   */
  handleAuthenticated() {
    if (this.navbar) this.navbar.classList.remove('hidden');
    if (this.sidebar) this.sidebar.classList.remove('hidden');
    if (this.mainContent) this.mainContent.classList.remove('hidden');

    // Initialize Chart canvases
    window.chartController.initThroughputChart();
    window.chartController.initTemperatureChart();

    // Load initial data
    this.switchView('dashboard');

    // Start periodic background data polling loop (every 3 seconds)
    this.startPolling();
  }

  /**
   * Handle UI state after logout
   */
  handleLoggedOut() {
    if (this.navbar) this.navbar.classList.add('hidden');
    if (this.sidebar) this.sidebar.classList.add('hidden');
    if (this.mainContent) this.mainContent.classList.add('hidden');

    if (window.authController) {
      window.authController.showLogin();
    }

    this.stopPolling();
  }

  /**
   * Switch active SPA view section
   * @param {string} viewName - 'dashboard' | 'sensors' | 'alerts'
   */
  switchView(viewName) {
    this.activeView = viewName;

    // Update sidebar active tab style
    this.navItems.forEach(item => {
      if (item.getAttribute('data-view') === viewName) {
        item.classList.add('active');
      } else {
        item.classList.remove('active');
      }
    });

    // Toggle view visibility
    this.viewSections.forEach(section => {
      if (section.id === `${viewName}-view`) {
        section.classList.remove('hidden');
      } else {
        section.classList.add('hidden');
      }
    });

    // Trigger page-specific data loading
    if (viewName === 'dashboard') {
      window.dashboardController.refreshData();
    } else if (viewName === 'sensors') {
      window.sensorsController.loadSensors();
    } else if (viewName === 'alerts') {
      window.alertsController.loadAlerts();
    }
  }

  /**
   * Toggle sidebar expanded/collapsed layout
   */
  toggleSidebar() {
    if (!this.sidebar || !this.mainContent) return;
    this.sidebar.classList.toggle('collapsed');
    this.mainContent.classList.toggle('sidebar-collapsed');
  }

  /**
   * Update live clock display every 1000ms
   */
  startClock() {
    const update = () => {
      if (this.clockElem) {
        const now = new Date();
        this.clockElem.textContent = `${now.toISOString().replace('T', ' ').substring(0, 19)} UTC`;
      }
    };
    update();
    setInterval(update, 1000);
  }

  /**
   * Start 3-second periodic telemetry polling tick
   */
  startPolling() {
    this.stopPolling();
    this.pollingInterval = setInterval(() => {
      if (this.activeView === 'dashboard') {
        window.dashboardController.refreshData();
      }
    }, 3000);
  }

  /**
   * Stop periodic telemetry polling tick
   */
  stopPolling() {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
      this.pollingInterval = null;
    }
  }
}

// Initialize application on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  window.app = new Application();
});
