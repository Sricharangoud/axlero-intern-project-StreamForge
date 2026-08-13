/* ==========================================================================
   STREAMFORGE FRONTEND - API CLIENT MODULE (js/api.js)
   ========================================================================== */

/**
 * ApiClient class handles HTTP requests using standard HTML5 Fetch API.
 * Features:
 * - Automatically attaches JWT Bearer token headers to requests
 * - Parses JSON responses and handles HTTP status codes
 * - Supports seamless offline fallback mock data generation for immediate UI testing
 */
class ApiClient {
  constructor() {
    this.baseURL = 'http://localhost:8000/api/v1'; // FastAPI backend base URL
    this.tokenKey = 'streamforge_jwt_token';
  }

  /**
   * Helper to retrieve stored JWT token from LocalStorage
   */
  getToken() {
    return localStorage.getItem(this.tokenKey);
  }

  /**
   * Helper to store JWT token upon successful login
   */
  setToken(token) {
    localStorage.setItem(this.tokenKey, token);
  }

  /**
   * Remove stored token on logout
   */
  removeToken() {
    localStorage.removeItem(this.tokenKey);
  }

  /**
   * Construct standard request headers, appending Bearer JWT authorization if available.
   */
  getHeaders() {
    const headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    };
    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
  }

  /**
   * Generic request method wrapper around HTML5 fetch()
   * @param {string} endpoint - API path (e.g. '/auth/login')
   * @param {object} options - Fetch options (method, body, headers)
   */
  async request(endpoint, options = {}) {
    const token = this.getToken();

    let targetEndpoint = endpoint;
    if (endpoint === '/stats/summary') {
      targetEndpoint = '/dashboard/summary';
    }

    // If using demo mock token, route requests directly to mock data handlers
    if (token && token.includes('mock') && targetEndpoint !== '/auth/login') {
      if (targetEndpoint === '/dashboard/summary' || targetEndpoint === '/stats/summary') return this.getMockDashboardData();
      if (targetEndpoint === '/sensors' || targetEndpoint === '/sensors/') return this.getMockSensorsList();
      if (targetEndpoint === '/alerts' || targetEndpoint === '/alerts/') return this.getMockAlertsList();
      if (targetEndpoint === '/streams/analytics') return this.getMockStreamAnalytics();
      if (targetEndpoint === '/streams/live') return this.getMockStreamAnalytics().top_streams;
      if (targetEndpoint === '/streams/simulate') return this.getMockSimulatedStream();
      if (targetEndpoint.includes('/acknowledge')) return { status: 'acknowledged' };
    }

    const url = `${this.baseURL}${targetEndpoint}`;
    const defaultHeaders = this.getHeaders();
    const config = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers
      }
    };

    try {
      const response = await fetch(url, config);

      // Handle HTTP status 401 (Unauthorized - invalid or expired token)
      if (response.status === 401) {
        // Only force logout if using a real token against real auth backend
        if (token && !token.includes('mock')) {
          this.removeToken();
          if (window.Toast) {
            window.Toast.show('Session expired. Please sign in again.', 'warning');
          }
          window.dispatchEvent(new Event('auth:unauthorized'));
        }
        throw new Error('Unauthorized');
      }

      // Handle non-2xx HTTP error status codes
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || `HTTP Error ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      // Return null or rethrow based on caller expectation
      console.warn(`[ApiClient] Request to ${endpoint} failed:`, error.message);
      throw error;
    }
  }

  /* ------------------------------------------------------------------------
     MOCK FALLBACK DATA GENERATORS (Used when backend is offline for immediate preview)
     ------------------------------------------------------------------------ */
  getMockDashboardData() {
    return {
      throughput: Math.floor(12000 + Math.random() * 3000),
      activeSensors: 48,
      totalSensors: 50,
      avgLatency: (3.8 + Math.random() * 0.8).toFixed(1),
      systemHealth: 99.9,
      temperatureCards: [
        { id: 'SNSR-001', zone: 'Processing Unit A', temp: (64 + Math.random() * 4).toFixed(1), status: 'NORMAL', maxTemp: 90 },
        { id: 'SNSR-002', zone: 'Kafka Cluster Node 1', temp: (78 + Math.random() * 5).toFixed(1), status: 'WARM', maxTemp: 90 },
        { id: 'SNSR-003', zone: 'PostgreSQL DB Host', temp: (86 + Math.random() * 6).toFixed(1), status: 'CRITICAL', maxTemp: 90 }
      ]
    };
  }

  getMockSensorsList() {
    return [
      { id: 'SNSR-001', location: 'Zone A - Server Rack 1', status: 'ONLINE', temp: 64.2, pressure: 14.7, battery: 98, lastPing: 'Just now' },
      { id: 'SNSR-002', location: 'Zone A - Server Rack 2', status: 'ONLINE', temp: 66.8, pressure: 14.8, battery: 95, lastPing: '2s ago' },
      { id: 'SNSR-003', location: 'Zone B - Kafka Cluster', status: 'WARNING', temp: 78.4, pressure: 15.2, battery: 88, lastPing: '5s ago' },
      { id: 'SNSR-004', location: 'Zone C - Database Host', status: 'ONLINE', temp: 86.1, pressure: 14.6, battery: 92, lastPing: '1s ago' },
      { id: 'SNSR-005', location: 'Zone D - Edge Ingress', status: 'OFFLINE', temp: 0.0, pressure: 0.0, battery: 0, lastPing: '15m ago' }
    ];
  }

  getMockAlertsList() {
    return [
      { id: 'ALT-901', severity: 'CRITICAL', source: 'SNSR-003', message: 'Temperature threshold exceeded (>85°C)', time: '18:54:12' },
      { id: 'ALT-902', severity: 'WARNING', source: 'SNSR-002', message: 'High Kafka partition lag detected', time: '18:50:05' },
      { id: 'ALT-903', severity: 'INFO', source: 'SYSTEM', message: 'Automated DB backup completed successfully', time: '18:30:00' }
    ];
  }

  getMockStreamAnalytics() {
    return {
      total_active_streams: 4,
      peak_concurrent_viewers: 6175,
      avg_bitrate_kbps: 6092.5,
      avg_dropped_frames_pct: 0.038,
      total_chat_velocity: 682.0,
      total_donations_usd: 1865.50,
      categories: [
        { category_name: 'Software Engineering', active_channels: 2, viewer_count: 2035 },
        { category_name: 'Cyberpunk 2077', active_channels: 1, viewer_count: 3250 },
        { category_name: 'Just Chatting', active_channels: 1, viewer_count: 890 }
      ],
      top_streams: [
        {
          id: 'str-001',
          channel_name: 'AliceCodes',
          streamer_name: 'Alice (Senior Eng)',
          stream_title: '🚀 Building Distributed Event Pipeline with FastAPI & Kafka',
          category: 'Software Engineering',
          viewer_count: 1420 + Math.floor(Math.random() * 50),
          peak_viewers: 1850,
          bitrate_kbps: 6120.0,
          fps: 60,
          resolution: '1080p60',
          dropped_frames_pct: 0.02,
          chat_velocity_ppm: 185.0,
          total_donations_usd: 350.0,
          avatar_color: '#6366f1'
        },
        {
          id: 'str-002',
          channel_name: 'BobTheGamer',
          streamer_name: 'Bob Pro',
          stream_title: '🎮 Cyberpunk 2077 Night City Speedrun [100% World Record]',
          category: 'Cyberpunk 2077',
          viewer_count: 3250 + Math.floor(Math.random() * 100),
          peak_viewers: 4100,
          bitrate_kbps: 6500.0,
          fps: 60,
          resolution: '1080p60',
          dropped_frames_pct: 0.08,
          chat_velocity_ppm: 340.0,
          total_donations_usd: 1240.0,
          avatar_color: '#ec4899'
        },
        {
          id: 'str-003',
          channel_name: 'DevTalksLive',
          streamer_name: 'Tech Community',
          stream_title: '💬 Software Architecture Q&A: Async Python vs Go Routines',
          category: 'Just Chatting',
          viewer_count: 890 + Math.floor(Math.random() * 30),
          peak_viewers: 1100,
          bitrate_kbps: 5800.0,
          fps: 60,
          resolution: '1080p60',
          dropped_frames_pct: 0.01,
          chat_velocity_ppm: 95.0,
          total_donations_usd: 180.5,
          avatar_color: '#10b981'
        },
        {
          id: 'str-004',
          channel_name: 'RustMechanic',
          streamer_name: 'Alex R',
          stream_title: '🦀 High-Performance Memory Safety in Systems Programming',
          category: 'Software Engineering',
          viewer_count: 615 + Math.floor(Math.random() * 20),
          peak_viewers: 750,
          bitrate_kbps: 5950.0,
          fps: 60,
          resolution: '1080p60',
          dropped_frames_pct: 0.04,
          chat_velocity_ppm: 62.0,
          total_donations_usd: 95.0,
          avatar_color: '#f59e0b'
        }
      ]
    };
  }

  getMockSimulatedStream() {
    const mock = this.getMockStreamAnalytics().top_streams[0];
    mock.viewer_count += 650;
    mock.peak_viewers += 650;
    mock.chat_velocity_ppm += 120;
    return mock;
  }
}

// Expose global API instance
window.apiClient = new ApiClient();
