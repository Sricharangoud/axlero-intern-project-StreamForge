/* ==========================================================================
   STREAMFORGE FRONTEND - SENSORS PAGE MODULE (js/sensors.js)
   ========================================================================== */

class SensorsController {
  constructor() {
    this.tableBody = document.getElementById('sensors-table-body');
    this.searchInput = document.getElementById('sensor-search-input');
    this.statusFilter = document.getElementById('sensor-status-filter');
    this.sensorsList = [];

    this.init();
  }

  init() {
    if (this.searchInput) {
      this.searchInput.addEventListener('input', () => this.applyFilters());
    }
    if (this.statusFilter) {
      this.statusFilter.addEventListener('change', () => this.applyFilters());
    }
  }

  /**
   * Load sensors fleet list from API or mock fallback
   */
  async loadSensors() {
    try {
      try {
        this.sensorsList = await window.apiClient.request('/sensors');
      } catch (e) {
        this.sensorsList = window.apiClient.getMockSensorsList();
      }

      this.renderTable(this.sensorsList);
    } catch (error) {
      console.error('Failed to load sensors list:', error);
    }
  }

  /**
   * Filter sensors list by query string & status dropdown
   */
  applyFilters() {
    const query = this.searchInput ? this.searchInput.value.toLowerCase().trim() : '';
    const status = this.statusFilter ? this.statusFilter.value : 'ALL';

    const filtered = this.sensorsList.filter(sensor => {
      const matchesQuery = sensor.id.toLowerCase().includes(query) || sensor.location.toLowerCase().includes(query);
      const matchesStatus = (status === 'ALL') || (sensor.status.toUpperCase() === status);
      return matchesQuery && matchesStatus;
    });

    this.renderTable(filtered);
  }

  /**
   * Render sensor data rows into table HTML
   * @param {Array} list - Filtered sensor list
   */
  renderTable(list) {
    if (!this.tableBody) return;

    if (!list || list.length === 0) {
      this.tableBody.innerHTML = `
        <tr>
          <td colspan="7" style="text-align:center; padding: 2rem; color: var(--text-dim);">
            No sensors found matching the selected criteria.
          </td>
        </tr>
      `;
      return;
    }

    this.tableBody.innerHTML = list.map(sensor => {
      const sensorId = sensor.sensor_code || sensor.id || 'SNSR-000';
      const status = sensor.status || (sensor.is_active ? 'ONLINE' : 'OFFLINE');
      const tempVal = sensor.temp !== undefined ? sensor.temp : (sensor.latest_reading !== undefined ? sensor.latest_reading : 65.0);
      const unit = sensor.metric_unit || '°C';
      const battery = sensor.battery !== undefined ? sensor.battery : 98;
      const lastPing = sensor.lastPing || (sensor.created_at ? new Date(sensor.created_at).toLocaleTimeString() : 'Just now');

      let badgeClass = 'badge-success';
      if (status === 'WARNING' || status === 'WARM') badgeClass = 'badge-warning';
      if (status === 'OFFLINE' || status === 'CRITICAL') badgeClass = 'badge-danger';

      return `
        <tr>
          <td><strong style="color: var(--text-primary);">${sensorId}</strong></td>
          <td>${sensor.location || 'Zone A'}</td>
          <td><span class="badge ${badgeClass}">${status}</span></td>
          <td><span style="color: var(--accent-cyan); font-weight:600;">${tempVal} ${unit}</span></td>
          <td>${sensor.pressure !== undefined ? sensor.pressure : 14.7} PSI</td>
          <td>
            <div style="display:flex; align-items:center; gap:8px;">
              <div style="width:50px; height:6px; background:var(--bg-dark-900); border-radius:3px; overflow:hidden;">
                <div style="width:${battery}%; height:100%; background:${battery > 20 ? 'var(--status-success)' : 'var(--status-danger)'};"></div>
              </div>
              <span style="font-size:0.8rem;">${battery}%</span>
            </div>
          </td>
          <td style="color: var(--text-secondary); font-size:0.85rem;">${lastPing}</td>
        </tr>
      `;
    }).join('');
  }
}

// Expose global Sensors Controller
window.sensorsController = new SensorsController();
