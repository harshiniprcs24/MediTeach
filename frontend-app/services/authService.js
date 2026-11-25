/**
 * MediTeach — Auth Service
 * =========================
 * Wraps the backend auth endpoints with clean, screen-friendly functions.
 *
 * All functions return either the data object on success, or an object
 * with { error: true, message: '...' } on failure. Screens never deal
 * with fetch or status codes directly.
 */

import api, { saveSession, clearSession, getAccessToken, getStoredUser } from './api';

/**
 * POST /auth/login
 *
 * Backend expects:  { email: string, password: string }
 * Backend returns:  { access_token, refresh_token, token_type, user: { id, name, email, ... } }
 *
 * @param {string} email
 * @param {string} password
 * @returns {Promise<{ success: true, user: object } | { error: true, message: string }>}
 */
export async function login(email, password) {
  const result = await api.post(
    '/auth/login',
    { email: email.trim().toLowerCase(), password },
    false, // login does not require a token
  );

  if (result.error) {
    return result;
  }

  // Persist the session
  await saveSession(result.access_token, result.refresh_token, result.user);

  return { success: true, user: result.user };
}

/**
 * Remove stored tokens and notify the backend (best-effort).
 * The backend /auth/logout endpoint returns 204 and discards nothing
 * server-side; token invalidation is purely client-side.
 */
export async function logout() {
  // Best-effort: notify backend. Ignore errors — we clear locally regardless.
  try {
    await api.post('/auth/logout', {}, true);
  } catch {
    // ignore
  }
  await clearSession();
}

/**
 * Check whether a stored, potentially valid session exists.
 * Returns the stored user object if a token is present, or null.
 *
 * NOTE: this does NOT validate the token against the server.
 * The token's validity is confirmed lazily on the first authenticated API call.
 * If that call returns 401, api.js attempts a refresh automatically.
 */
export async function getStoredSession() {
  const token = await getAccessToken();
  if (!token) return null;
  const user = await getStoredUser();
  return user ? { token, user } : null;
}
