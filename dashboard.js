/* ==========================================================================
   STREAMFORGE FRONTEND - DASHBOARD VIEW MODULE (js/dashboard.js)
   ========================================================================== */

class DashboardController {
  constructor() {
    this.throughputElem = document.getElementById('stat-throughput');
    this.activeSensorsElem = document.getElementById('stat-active-sensors');
    this.latencyElem = document.getElementById('stat-latency');
    this.healthElem = document.getElementById('stat-health');
    this.tempCardsContainer = document.getElementById('temperature-cards-container');
    this.refreshBtn = document.getElementById('refresh-dashboard-btn');

    this.init();
  }

  init() {
    if (this.refreshBtn) {
      this.refreshBtn.addEventListener('click', () => this.refreshData());
    }
  }

  /**
   * Fetch latest metrics from FastAPI or mock fallback & update UI
   */
  async refreshData() {
    try {
      // Fetch telemetry from API (or fallback mock)
      let data;
      try {
        data = await window.apiClient.request('/stats/summary');
      } catch (e) {
        data = window.apiClient.getMockDashboardData();
      }

      this.updateStatsCards(data);
      this.renderTemperatureCards(data.temperatureCards);

      // Push latest throughput to Chart.js
      const now = new Date();
      const timeStr = now.toTimeString().split(' ')[0];
      window.chartController.updateThroughput(timeStr, data.throughput);

    } catch (error) {
      console.error('Failed to update dashboard:', error);
    }
  }

  /**
   * Update top 4 Statistics Cards DOM content
   */
  updateStatsCards(data) {
    if (this.throughputElem) {
      this.throughputElem.textContent = data.throughput.toLocaleString();
    }
    if (this.activeSensorsElem) {
      this.activeSensorsElem.textContent = `${data.activeSensors} / ${data.totalSensors}`;
    }
    if (this.latencyElem) {
      this.latencyElem.textContent = `${data.avgLatency} ms`;
    }
    if (this.healthElem) {
      this.healthElem.textContent = `${data.systemHealth}%`;
    }
  }

  /**
   * Dynamically generate Temperature Cards DOM HTML
   * @param {Array} cards - Array of sensor temperature objects
   */
  renderTemperatureCards(cards) {
    if (!this.tempCardsContainer || !cards) return;

    this.tempCardsContainer.innerHTML = '';

    cards.forEach(card => {
      const percentage = Math.min(100, Math.round((card.temp / card.maxTemp) * 100));
      
      let badgeClass = 'badge-success';
      if (card.status === 'WARM') badgeClass = 'badge-warning';
      if (card.status === 'CRITICAL') badgeClass = 'badge-danger';

      const cardElem = document.createElement('div');
      cardElem.className = 'card';
      cardElem.innerHTML = `
        <div class="temp-card-header">
          <div>
            <span class="temp-sensor-id">${card.id}</span>
            <div style="font-size: 0.8rem; color: var(--text-secondary);">${card.zone}</div>
          </div>
          <span class="badge ${badgeClass}">${card.status}</span>
        </div>

        <div class="temp-gauge-display">
          <span class="temp-number">${card.temp}</span>
          <span class="temp-unit">°C</span>
        </div>

        <div class="temp-bar-container">
          <div class="temp-bar-fill" style="width: ${percentage}%;"></div>
        </div>
      `;

      this.tempCardsContainer.appendChild(cardElem);
    });
  }
}

// Expose global Dashboard controller
window.dashboardController = new DashboardController();
