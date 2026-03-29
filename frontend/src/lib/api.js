export async function apiFetch(path, options = {}) {
  const { token, headers, body, ...rest } = options;
  const requestHeaders = new Headers(headers ?? {});

  if (token) {
    requestHeaders.set('Authorization', `Bearer ${token}`);
  }

  if (body && !(body instanceof FormData) && !requestHeaders.has('Content-Type')) {
    requestHeaders.set('Content-Type', 'application/json');
  }

  const response = await fetch(path, {
    ...rest,
    body,
    headers: requestHeaders,
  });

  if (!response.ok) {
    let message = 'リクエストに失敗しました';

    try {
      const errorPayload = await response.json();
      if (typeof errorPayload?.detail === 'string') {
        message = errorPayload.detail;
      }
    } catch {
      // JSON でないエラーは既定文言を使う
    }

    throw new Error(message);
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}
