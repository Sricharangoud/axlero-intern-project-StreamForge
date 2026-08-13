/* ==========================================================================
   STREAMFORGE FRONTEND - LIVE STREAMS MODULE (js/streams.js)
   ========================================================================== */

class StreamsManager {
  constructor() {
    this.streams = [];
    this.analytics = null;
    this.initialized = false;
  }

  /**
   * Initialize module event listeners
   */
  init() {
    if (this.initialized) return;
    this.initialized = true;

    const refreshBtn = document.getElementById('refresh-streams-btn');
    if (refreshBtn) {
      refreshBtn.addEventListener('click', () => {
        this.loadStreamTelemetry();
        if (window.Toast) window.Toast.show('Live stream telemetry updated', 'info');
      });
    }

    const simulateBtn = document.getElementById('simulate-spike-btn');
    if (simulateBtn) {
      simulateBtn.addEventListener('click', () => this.simulateSpike());
    }

    // Initial load
    this.loadStreamTelemetry();
  }

  /**
   * Fetch stream telemetry from backend API
   */
  async loadStreamTelemetry() {
    try {
      const data = await window.apiClient.request('/streams/analytics');
      if (data) {
        this.analytics = data;
        this.streams = data.top_streams || [];
        this.updateStatsCounters(data);
        this.renderStreamCards(this.streams);

        if (window.chartController) {
          window.chartController.initStreamBitrateChart(this.streams);
          window.chartController.initStreamChatChart(this.streams);
        }
      }
    } catch (err) {
      console.warn('[StreamsManager] Failed to load stream telemetry:', err);
    }
  }

  /**
   * Update top summary stat cards
   */
  updateStatsCounters(data) {
    const streamCountEl = document.getElementById('stat-stream-count');
    const viewersEl = document.getElementById('stat-stream-viewers');
    const bitrateEl = document.getElementById('stat-stream-bitrate');
    const chatEl = document.getElementById('stat-stream-chat');
    const donationsEl = document.getElementById('stat-stream-donations');

    if (streamCountEl) streamCountEl.textContent = data.total_active_streams || 0;
    if (viewersEl) viewersEl.textContent = (data.peak_concurrent_viewers || 0).toLocaleString();
    if (bitrateEl) bitrateEl.textContent = `${(data.avg_bitrate_kbps || 0).toLocaleString()} kbps`;
    if (chatEl) chatEl.textContent = `${data.total_chat_velocity || 0} msg/m`;
    if (donationsEl) donationsEl.textContent = `$${(data.total_donations_usd || 0).toLocaleString()}`;
  }

  /**
   * Render dynamic broadcast cards
   */
  renderStreamCards(streams) {
    const grid = document.getElementById('live-streams-grid');
    if (!grid) return;

    if (!streams || streams.length === 0) {
      grid.innerHTML = '<p style="color: var(--text-dim);">No active stream broadcasts currently detected.</p>';
      return;
    }

    grid.innerHTML = streams.map(stream => {
      const avatarColor = stream.avatar_color || '#6366f1';
      const initial = stream.channel_name ? stream.channel_name.charAt(0).toUpperCase() : 'S';
      const droppedFramesText = `${(stream.dropped_frames_pct || 0).toFixed(2)}%`;
      const droppedFramesColor = stream.dropped_frames_pct > 1.0 ? '#ef4444' : '#10b981';

      return `
        <div class="card" style="border-left: 4px solid ${avatarColor}; padding: 1.25rem;">
          <div class="flex-between" style="margin-bottom: 0.75rem;">
            <div style="display: flex; align-items: center; gap: 12px;">
              <div class="avatar-circle" style="background: ${avatarColor}; font-weight: 700; width: 42px; height: 42px; font-size: 1.1rem;">
                ${initial}
              </div>
              <div>
                <h3 style="font-size: 1.05rem; font-weight: 700; color: var(--text-primary); margin: 0;">
                  ${stream.channel_name}
                </h3>
                <span style="font-size: 0.8rem; color: var(--text-secondary);">${stream.streamer_name}</span>
              </div>
            </div>
            <span class="badge" style="background: rgba(239, 68, 68, 0.15); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3);">
              <i class="fa-solid fa-circle" style="font-size: 0.5rem; margin-right: 4px; vertical-align: middle;"></i> LIVE
            </span>
          </div>

          <h4 style="font-size: 0.95rem; font-weight: 600; color: var(--text-primary); margin-bottom: 0.75rem; line-height: 1.3;">
            ${stream.stream_title}
          </h4>

          <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 1rem;">
            <span class="badge badge-info">${stream.category}</span>
            <span class="badge badge-success">${stream.resolution}</span>
            <span class="badge badge-info" style="background: rgba(99, 102, 241, 0.15); color: #818cf8;">
              <i class="fa-solid fa-gauge-high"></i> ${(stream.bitrate_kbps || 0).toLocaleString()} kbps
            </span>
          </div>

          <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; background: rgba(0, 0, 0, 0.2); padding: 0.75rem; border-radius: 8px; font-size: 0.82rem;">
            <div>
              <span style="color: var(--text-dim); display: block;">Concurrent Viewers</span>
              <strong style="color: var(--text-primary); font-size: 0.95rem;">
                <i class="fa-solid fa-user" style="color: var(--accent-cyan);"></i> ${(stream.viewer_count || 0).toLocaleString()}
              </strong>
            </div>
            <div>
              <span style="color: var(--text-dim); display: block;">Chat Velocity</span>
              <strong style="color: var(--text-primary); font-size: 0.95rem;">
                <i class="fa-solid fa-message" style="color: var(--accent-emerald);"></i> ${stream.chat_velocity_ppm} m/m
              </strong>
            </div>
            <div>
              <span style="color: var(--text-dim); display: block;">Dropped Frames</span>
              <strong style="color: ${droppedFramesColor}; font-size: 0.95rem;">
                <i class="fa-solid fa-chart-line"></i> ${droppedFramesText}
              </strong>
            </div>
          </div>
        </div>
      `;
    }).join('');
  }

  /**
   * Interactive reviewer simulation trigger
   */
  async simulateSpike() {
    try {
      if (window.Toast) window.Toast.show('Simulating live viewer & traffic burst...', 'warning');
      await window.apiClient.request('/streams/simulate', {
        method: 'POST',
        body: JSON.stringify({ action: 'viewer_spike', magnitude: 2.0 })
      });
      await this.loadStreamTelemetry();
      if (window.Toast) window.Toast.show('⚡ Viewer spike simulated! Viewers & Chat Velocity updated.', 'success');
    } catch (err) {
      console.warn('[StreamsManager] Simulation failed:', err);
    }
  }
}

// Instantiate global streams manager
window.streamsManager = new StreamsManager();
