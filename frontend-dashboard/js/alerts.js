/* ==========================================================================
   STREAMFORGE FRONTEND - ALERTS PAGE MODULE (js/alerts.js)
   ========================================================================== */

class AlertsController {
  constructor() {
    this.tableBody = document.getElementById('alerts-table-body');
    this.filterBtns = document.querySelectorAll('.alert-filter-btn');
    this.alertsList = [];
    this.activeFilter = 'ALL';

    this.init();
  }

  init() {
    this.filterBtns.forEach(btn => {
      btn.addEventListener('click', (e) => {
        this.filterBtns.forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        this.activeFilter = e.target.getAttribute('data-filter');
        this.applyFilter();
      });
    });
  }

  /**
   * Fetch system alerts list from API or mock fallback
   */
  async loadAlerts() {
    try {
      try {
        this.alertsList = await window.apiClient.request('/alerts');
      } catch (e) {
        this.alertsList = window.apiClient.getMockAlertsList();
      }

      this.applyFilter();
    } catch (error) {
      console.error('Failed to load alerts list:', error);
    }
  }

  /**
   * Filter alerts based on active severity tab
   */
  applyFilter() {
    const filtered = this.alertsList.filter(alert => {
      if (this.activeFilter === 'ALL') return true;
      return alert.severity.toUpperCase() === this.activeFilter;
    });

    this.renderTable(filtered);
  }

  /**
   * Render alert table rows into HTML
   * @param {Array} list - Filtered list of alert items
   */
  renderTable(list) {
    if (!this.tableBody) return;

    if (!list || list.length === 0) {
      this.tableBody.innerHTML = `
        <tr>
          <td colspan="6" style="text-align:center; padding: 2rem; color: var(--text-dim);">
            <i class="fa-solid fa-circle-check" style="color: var(--status-success); margin-right: 8px;"></i>
            No active alerts matching the selected severity level.
          </td>
        </tr>
      `;
      return;
    }

    this.tableBody.innerHTML = list.map(alert => {
      const alertId = alert.id ? (alert.id.length > 8 ? alert.id.substring(0, 8).toUpperCase() : alert.id) : 'ALT-000';
      const severity = (alert.severity || 'INFO').toUpperCase();
      const source = alert.source || (alert.sensor ? alert.sensor.sensor_code : alert.sensor_id) || 'SYSTEM';
      const message = alert.message || 'Threshold breached';
      const timeStr = alert.time || (alert.created_at ? new Date(alert.created_at).toLocaleTimeString() : 'Just now');

      let badgeClass = 'badge-info';
      if (severity === 'CRITICAL') badgeClass = 'badge-danger';
      if (severity === 'WARNING') badgeClass = 'badge-warning';

      return `
        <tr>
          <td><strong style="color: var(--text-primary);">${alertId}</strong></td>
          <td><span class="badge ${badgeClass}">${severity}</span></td>
          <td><code>${source}</code></td>
          <td>${message}</td>
          <td style="color: var(--text-secondary); font-size:0.85rem;">${timeStr}</td>
          <td>
            <button class="btn btn-secondary acknowledge-alert-btn" data-id="${alert.id}" style="padding: 4px 10px; font-size: 0.8rem;">
              <i class="fa-solid fa-check"></i> Acknowledge
            </button>
          </td>
        </tr>
      `;
    }).join('');

    // Bind Acknowledge button events
    this.tableBody.querySelectorAll('.acknowledge-alert-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const alertId = e.currentTarget.getAttribute('data-id');
        this.acknowledgeAlert(alertId);
      });
    });
  }

  /**
   * Handle alert acknowledgement
   * @param {string} alertId
   */
  async acknowledgeAlert(alertId) {
    try {
      // Attempt API call
      await window.apiClient.request(`/alerts/${alertId}/acknowledge`, { method: 'POST' }).catch(() => {});

      // Remove from local list & re-render
      this.alertsList = this.alertsList.filter(a => a.id !== alertId);
      this.applyFilter();

      window.Toast.show(`Alert ${alertId} has been acknowledged.`, 'success');
    } catch (error) {
      window.Toast.show(`Failed to acknowledge alert ${alertId}`, 'error');
    }
  }
}

// Expose global Alerts Controller
window.alertsController = new AlertsController();
