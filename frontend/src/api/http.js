const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '');


export async function request(path, options = {}) {
  const controller = new AbortController();
  const timeoutId = window.setTimeout(() => controller.abort(), 15000);
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      signal: options.signal || controller.signal,
      headers: options.body
        ? { 'Content-Type': 'application/json', ...(options.headers || {}) }
        : { ...(options.headers || {}) },
    });
    if (response.status === 204) return null;
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      const error = new Error(payload.detail || '요청을 처리하지 못했습니다.');
      error.status = response.status;
      throw error;
    }
    return payload;
  } finally {
    window.clearTimeout(timeoutId);
  }
}
