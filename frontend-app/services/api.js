/**
 * MediTeach — Centralized API Service
 * =====================================
 * All backend communication goes through this module.
 *
 * Base URL is read from the EXPO_PUBLIC_API_BASE_URL environment variable
 * defined in frontend-app/.env — never hardcoded here.
 *
 * Usage:
 *   import api from '../services/api';
 *
 *   // Unauthenticated request (login, register)
 *   const data = await api.post('/auth/login', { email, password });
 *
 *   // Authenticated request (token injected automatically)
 *   const data = await api.get('/medicines/search?q=paracetamol');
 *
 * Error shape returned on failure:
 *   { error: true, status: <http_status>, message: '<human-readable>' }
 */

import AsyncStorage from '@react-native-async-storage/async-storage';

// ── Configuration ─────────────────────────────────────────────────────────────
const BASE_URL = process.env.EXPO_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

// AsyncStorage keys — centralised so nothing is scattered across screens
export const STORAGE_KEYS = {
  ACCESS_TOKEN:  'mediteach_access_token',
  REFRESH_TOKEN: 'mediteach_refresh_token',
  USER:          'mediteach_user',
};

// ── Token helpers ─────────────────────────────────────────────────────────────

/**
 * Save tokens and user object returned by login or register.
 * @param {string} accessToken
 * @param {string} refreshToken
 * @param {object} user
 */
export async function saveSession(accessToken, refreshToken, user) {
  // Use individual setItem calls — compatible with both v2 and v3 of
  // @react-native-async-storage/async-storage (multiSet was removed in v3).
  await AsyncStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN,  accessToken);
  await AsyncStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, refreshToken);
  await AsyncStorage.setItem(STORAGE_KEYS.USER,          JSON.stringify(user));
}

/**
 * Remove all stored auth data. Call on logout or 401 with expired refresh.
 */
export async function clearSession() {
  // Use individual removeItem calls — compatible with both v2 and v3
  // (multiRemove was removed in v3).
  await AsyncStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
  await AsyncStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
  await AsyncStorage.removeItem(STORAGE_KEYS.USER);
}

/**
 * Read the stored access token (or null if not present).
 */
export async function getAccessToken() {
  return AsyncStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
}

/**
 * Read the stored refresh token (or null if not present).
 */
export async function getRefreshToken() {
  return AsyncStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN);
}

/**
 * Read the stored user object (or null).
 */
export async function getStoredUser() {
  const raw = await AsyncStorage.getItem(STORAGE_KEYS.USER);
  return raw ? JSON.parse(raw) : null;
}

// ── Token refresh ─────────────────────────────────────────────────────────────

let _refreshPromise = null; // prevents concurrent refresh races

async function attemptTokenRefresh() {
  // Only one refresh in flight at a time
  if (_refreshPromise) return _refreshPromise;

  _refreshPromise = (async () => {
    try {
      const refreshToken = await getRefreshToken();
      if (!refreshToken) return null;

      const response = await fetch(`${BASE_URL}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (!response.ok) {
        await clearSession();
        return null;
      }

      const data = await response.json();
      await saveSession(data.access_token, data.refresh_token, data.user);
      return data.access_token;
    } catch {
      await clearSession();
      return null;
    } finally {
      _refreshPromise = null;
    }
  })();

  return _refreshPromise;
}

// ── Core request function ─────────────────────────────────────────────────────

/**
 * Make an HTTP request to the backend.
 *
 * @param {string} method    - 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'
 * @param {string} path      - URL path, e.g. '/auth/login' or '/medicines/search?q=aspirin'
 * @param {object} [body]    - JSON request body (omit for GET/DELETE)
 * @param {boolean} [auth]   - Whether to attach Authorization header (default: true)
 * @param {boolean} [_retry] - Internal flag: true when retrying after token refresh
 * @returns {Promise<object>} Parsed JSON response, or error object on failure
 */
async function request(method, path, body = null, auth = true, _retry = false) {
  const headers = { 'Content-Type': 'application/json' };

  if (auth) {
    const token = await getAccessToken();
    if (token) {
      // Token value is never logged — only its presence is confirmed
      headers['Authorization'] = `Bearer ${token}`;
    }
  }

  const options = { method, headers };
  if (body !== null && method !== 'GET' && method !== 'DELETE') {
    options.body = JSON.stringify(body);
  }

  let response;
  try {
    response = await fetch(`${BASE_URL}${path}`, options);
  } catch (networkError) {
    // Network unreachable — backend not running or wrong IP
    return {
      error: true,
      status: 0,
      message: 'Cannot reach the server. Check that the backend is running and EXPO_PUBLIC_API_BASE_URL is correct.',
    };
  }

  // 204 No Content — return success with no body
  if (response.status === 204) {
    return { success: true };
  }

  // Attempt to parse JSON body
  let data;
  try {
    data = await response.json();
  } catch {
    return {
      error: true,
      status: response.status,
      message: `Server returned status ${response.status} with non-JSON body.`,
    };
  }

  // Token expired — try one refresh then retry original request
  if (response.status === 401 && !_retry) {
    const newToken = await attemptTokenRefresh();
    if (newToken) {
      return request(method, path, body, auth, true);
    }
    // Refresh failed — session is cleared, caller must navigate to login
    return {
      error: true,
      status: 401,
      message: 'Session expired. Please log in again.',
      sessionExpired: true,
    };
  }

  if (!response.ok) {
    return {
      error: true,
      status: response.status,
      message: data?.detail || `Request failed with status ${response.status}.`,
    };
  }

  return data;
}

// ── Public API surface ────────────────────────────────────────────────────────

const api = {
  /**
   * GET request (authenticated by default).
   * @param {string} path
   * @param {boolean} [auth=true]
   */
  get: (path, auth = true) => request('GET', path, null, auth),

  /**
   * POST request.
   * @param {string} path
   * @param {object} body
   * @param {boolean} [auth=true]
   */
  post: (path, body, auth = true) => request('POST', path, body, auth),

  /**
   * PUT request.
   * @param {string} path
   * @param {object} body
   * @param {boolean} [auth=true]
   */
  put: (path, body, auth = true) => request('PUT', path, body, auth),

  /**
   * PATCH request.
   * @param {string} path
   * @param {object} body
   * @param {boolean} [auth=true]
   */
  patch: (path, body, auth = true) => request('PATCH', path, body, auth),

  /**
   * DELETE request.
   * @param {string} path
   * @param {boolean} [auth=true]
   */
  delete: (path, auth = true) => request('DELETE', path, null, auth),

  /**
   * Upload a file using multipart/form-data.
   * Used for POST /prescriptions/upload.
   *
   * @param {string} path         - e.g. '/prescriptions/upload?language=en'
   * @param {FormData} formData   - FormData object with the file appended
   * @returns {Promise<object>}   Parsed JSON response or error object
   */
  uploadFile: async (path, formData) => {
    const token = await getAccessToken();
    const headers = {};
    // Do NOT set Content-Type — the browser/fetch sets it automatically
    // with the correct multipart boundary when body is FormData.
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    let response;
    try {
      response = await fetch(`${BASE_URL}${path}`, {
        method: 'POST',
        headers,
        body: formData,
      });
    } catch {
      return {
        error: true,
        status: 0,
        message: 'Cannot reach the server. Check that the backend is running and EXPO_PUBLIC_API_BASE_URL is correct.',
      };
    }

    let data;
    try {
      data = await response.json();
    } catch {
      return {
        error: true,
        status: response.status,
        message: `Server returned status ${response.status} with non-JSON body.`,
      };
    }

    if (response.status === 401) {
      const newToken = await attemptTokenRefresh();
      if (newToken) {
        return api.uploadFile(path, formData);
      }
      return {
        error: true,
        status: 401,
        message: 'Session expired. Please log in again.',
        sessionExpired: true,
      };
    }

    if (!response.ok) {
      return {
        error: true,
        status: response.status,
        message: data?.detail || `Upload failed with status ${response.status}.`,
      };
    }

    return data;
  },
};

export default api;
