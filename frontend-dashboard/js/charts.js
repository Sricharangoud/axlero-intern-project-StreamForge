/* ==========================================================================
   STREAMFORGE FRONTEND - CHART.JS CONTROLLER MODULE (js/charts.js)
   Supports dynamic light/dark theme adaptation for high-contrast telemetry.
   ========================================================================== */

class ChartController {
  constructor() {
    this.throughputChart = null;
    this.temperatureChart = null;
    this.streamBitrateChart = null;
    this.streamChatChart = null;

    // Listen for theme change events
    window.addEventListener('theme:changed', (e) => {
      this.updateTheme(e.detail.theme);
    });
  }

  /**
   * Get colors based on active theme
   */
  getThemeColors(theme = null) {
    const isLight = (theme || document.documentElement.getAttribute('data-theme')) === 'light';
    return {
      textColor: isLight ? '#475569' : '#a1a1aa',
      gridColor: isLight ? 'rgba(0, 0, 0, 0.07)' : 'rgba(255, 255, 255, 0.06)',
      tooltipBg: isLight ? '#ffffff' : '#000000',
      tooltipText: isLight ? '#0f172a' : '#ffffff',
      tooltipBorder: isLight ? 'rgba(0, 0, 0, 0.12)' : '#262626',
      lineColor: isLight ? '#2563eb' : '#38bdf8',
      lineFillBg: isLight ? 'rgba(37, 99, 235, 0.12)' : 'rgba(56, 189, 248, 0.08)',
    };
  }

  /**
   * Apply universal theme-aware defaults to Chart.js global config
   */
  applyGlobalDefaults(theme = null) {
    if (typeof Chart === 'undefined') return;

    const colors = this.getThemeColors(theme);
    Chart.defaults.color = colors.textColor;
    Chart.defaults.font.family = "'Inter', -apple-system, sans-serif";
    Chart.defaults.plugins.tooltip.backgroundColor = colors.tooltipBg;
    Chart.defaults.plugins.tooltip.titleColor = colors.tooltipText;
    Chart.defaults.plugins.tooltip.bodyColor = colors.tooltipText;
    Chart.defaults.plugins.tooltip.borderColor = colors.tooltipBorder;
    Chart.defaults.plugins.tooltip.borderWidth = 1;
    Chart.defaults.plugins.tooltip.padding = 10;
  }

  /**
   * Update existing chart instances when theme changes
   */
  updateTheme(theme) {
    if (typeof Chart === 'undefined') return;

    this.applyGlobalDefaults(theme);
    const colors = this.getThemeColors(theme);

    const updateChartColors = (chart) => {
      if (!chart) return;
      if (chart.options.scales.x && chart.options.scales.x.grid) {
        if (chart.options.scales.x.grid.display !== false) {
          chart.options.scales.x.grid.color = colors.gridColor;
        }
      }
      if (chart.options.scales.y && chart.options.scales.y.grid) {
        if (chart.options.scales.y.grid.display !== false) {
          chart.options.scales.y.grid.color = colors.gridColor;
        }
      }
      chart.update();
    };

    updateChartColors(this.throughputChart);
    updateChartColors(this.temperatureChart);
    updateChartColors(this.streamBitrateChart);
    updateChartColors(this.streamChatChart);
  }

  /**
   * Initialize Event Throughput Line Chart
   */
  initThroughputChart() {
    const ctx = document.getElementById('throughputChart');
    if (!ctx) return;

    this.applyGlobalDefaults();
    const colors = this.getThemeColors();

    if (this.throughputChart) {
      this.throughputChart.destroy();
    }

    const labels = ['18:50', '18:51', '18:52', '18:53', '18:54', '18:55', '18:56', '18:57', '18:58', '18:59'];
    const initialData = [11200, 12400, 13100, 12800, 14200, 13900, 14500, 14100, 14800, 15200];

    this.throughputChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [{
          label: 'Events Processed / sec',
          data: initialData,
          borderColor: colors.lineColor,
          backgroundColor: colors.lineFillBg,
          borderWidth: 2,
          fill: true,
          tension: 0.4,
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
            grid: { color: colors.gridColor }
          },
          y: {
            grid: { color: colors.gridColor },
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

    const colors = this.getThemeColors();

    if (this.temperatureChart) {
      this.temperatureChart.destroy();
    }

    const sensorIds = ['SNSR-001', 'SNSR-002', 'SNSR-003', 'SNSR-004', 'SNSR-005'];
    const temps = [64.2, 78.4, 86.1, 71.0, 58.5];
    const backgroundColors = temps.map(t => {
      if (t >= 85) return '#ef4444';
      if (t >= 75) return '#f59e0b';
      return '#06b6d4';
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
            grid: { color: colors.gridColor },
            suggestedMax: 100
          }
        }
      }
    });
  }

  /**
   * Append new throughput data point in real time
   */
  updateThroughput(timestamp, value) {
    if (!this.throughputChart) return;

    const labels = this.throughputChart.data.labels;
    const data = this.throughputChart.data.datasets[0].data;

    if (labels.length >= 12) {
      labels.shift();
      data.shift();
    }

    labels.push(timestamp);
    data.push(value);
    this.throughputChart.update('none');
  }

  /**
   * Initialize Live Stream Encoding Bitrate Bar/Line Chart
   */
  initStreamBitrateChart(streams = []) {
    const ctx = document.getElementById('streamBitrateChart');
    if (!ctx) return;

    this.applyGlobalDefaults();
    const colors = this.getThemeColors();

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
          y: { grid: { color: colors.gridColor }, suggestedMax: 8000 }
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

    const colors = this.getThemeColors();

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
          x: { grid: { color: colors.gridColor } },
          y: { grid: { color: colors.gridColor }, beginAtZero: true }
        }
      }
    });
  }
}

// Expose global Chart Controller
window.chartController = new ChartController();
