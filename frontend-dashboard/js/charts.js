/* ==========================================================================
   STREAMFORGE FRONTEND - CHART.JS CONTROLLER MODULE (js/charts.js)
   ========================================================================== */

class ChartController {
  constructor() {
    this.throughputChart = null;
    this.temperatureChart = null;
  }

  /**
   * Apply universal dark mode defaults to Chart.js global config
   */
  applyGlobalDefaults() {
    if (typeof Chart === 'undefined') return;

    Chart.defaults.color = '#9ca3af'; // Muted label color
    Chart.defaults.font.family = "'Inter', sans-serif";
    Chart.defaults.plugins.tooltip.backgroundColor = '#1f293d';
    Chart.defaults.plugins.tooltip.titleColor = '#f3f4f6';
    Chart.defaults.plugins.tooltip.borderColor = 'rgba(255, 255, 255, 0.1)';
    Chart.defaults.plugins.tooltip.borderWidth = 1;
    Chart.defaults.plugins.tooltip.padding = 10;
  }

  /**
   * Initialize Event Throughput Line Chart
   */
  initThroughputChart() {
    const ctx = document.getElementById('throughputChart');
    if (!ctx) return;

    this.applyGlobalDefaults();

    // Initial 10 time labels
    const labels = ['18:50', '18:51', '18:52', '18:53', '18:54', '18:55', '18:56', '18:57', '18:58', '18:59'];
    const initialData = [11200, 12400, 13100, 12800, 14200, 13900, 14500, 14100, 14800, 15200];

    this.throughputChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [{
          label: 'Events Processed / sec',
          data: initialData,
          borderColor: '#3b82f6',
          backgroundColor: 'rgba(59, 130, 246, 0.12)',
          borderWidth: 2,
          fill: true,
          tension: 0.4, // Smooth curve
          pointRadius: 3,
          pointHoverRadius: 6,
          pointBackgroundColor: '#06b6d4'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          x: {
            grid: { color: 'rgba(255, 255, 255, 0.05)' }
          },
          y: {
            grid: { color: 'rgba(255, 255, 255, 0.05)' },
            beginAtZero: false
          }
        }
      }
    });
  }

  /**
   * Initialize Sensor Temperature Distribution Bar Chart
   */
  initTemperatureChart() {
    const ctx = document.getElementById('temperatureChart');
    if (!ctx) return;

    const sensorIds = ['SNSR-001', 'SNSR-002', 'SNSR-003', 'SNSR-004', 'SNSR-005'];
    const temps = [64.2, 78.4, 86.1, 71.0, 58.5];
    const backgroundColors = temps.map(t => {
      if (t >= 85) return '#ef4444'; // Red for critical temp
      if (t >= 75) return '#f59e0b'; // Amber for warning
      return '#06b6d4';              // Cyan for normal
    });

    this.temperatureChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: sensorIds,
        datasets: [{
          label: 'Temperature (°C)',
          data: temps,
          backgroundColor: backgroundColors,
          borderRadius: 6,
          borderSkipped: false
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          x: {
            grid: { display: false }
          },
          y: {
            grid: { color: 'rgba(255, 255, 255, 0.05)' },
            suggestedMax: 100
          }
        }
      }
    });
  }

  /**
   * Append new throughput data point in real time
   * @param {string} timestamp - Current time label (e.g. '19:00:05')
   * @param {number} value - New throughput count
   */
  updateThroughput(timestamp, value) {
    if (!this.throughputChart) return;

    const labels = this.throughputChart.data.labels;
    const data = this.throughputChart.data.datasets[0].data;

    // Maintain max 12 data points sliding window
    if (labels.length >= 12) {
      labels.shift();
      data.shift();
    }

    labels.push(timestamp);
    data.push(value);
    this.throughputChart.update('none'); // Update smoothly without full redraw animation
  }

  /**
   * Initialize Live Stream Encoding Bitrate Bar/Line Chart
   */
  initStreamBitrateChart(streams = []) {
    const ctx = document.getElementById('streamBitrateChart');
    if (!ctx) return;

    this.applyGlobalDefaults();

    const channelNames = streams.length ? streams.map(s => s.channel_name) : ['AliceCodes', 'BobTheGamer', 'DevTalksLive', 'RustMechanic'];
    const bitrates = streams.length ? streams.map(s => s.bitrate_kbps) : [6120, 6500, 5800, 5950];

    if (this.streamBitrateChart) {
      this.streamBitrateChart.data.labels = channelNames;
      this.streamBitrateChart.data.datasets[0].data = bitrates;
      this.streamBitrateChart.update();
      return;
    }

    this.streamBitrateChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: channelNames,
        datasets: [{
          label: 'Bitrate (kbps)',
          data: bitrates,
          backgroundColor: ['#6366f1', '#ec4899', '#10b981', '#f59e0b'],
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { display: false } },
          y: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, suggestedMax: 8000 }
        }
      }
    });
  }

  /**
   * Initialize Stream Chat Velocity & Viewer Chart
   */
  initStreamChatChart(streams = []) {
    const ctx = document.getElementById('streamChatChart');
    if (!ctx) return;

    const channelNames = streams.length ? streams.map(s => s.channel_name) : ['AliceCodes', 'BobTheGamer', 'DevTalksLive', 'RustMechanic'];
    const chatRates = streams.length ? streams.map(s => s.chat_velocity_ppm) : [185, 340, 95, 62];

    if (this.streamChatChart) {
      this.streamChatChart.data.labels = channelNames;
      this.streamChatChart.data.datasets[0].data = chatRates;
      this.streamChatChart.update();
      return;
    }

    this.streamChatChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: channelNames,
        datasets: [{
          label: 'Chat Velocity (msgs/min)',
          data: chatRates,
          borderColor: '#10b981',
          backgroundColor: 'rgba(16, 185, 129, 0.15)',
          fill: true,
          tension: 0.3,
          pointRadius: 4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: 'rgba(255, 255, 255, 0.05)' } },
          y: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, beginAtZero: true }
        }
      }
    });
  }
}

// Expose global Chart Controller
window.chartController = new ChartController();
