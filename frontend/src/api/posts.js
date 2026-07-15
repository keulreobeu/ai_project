import { request } from './http';


export function fetchPosts({ page = 1, limit = 20, q = '' } = {}) {
  const params = new URLSearchParams({ page, limit });
  if (q) params.set('q', q);
  return request(`/api/posts?${params.toString()}`);
}

export function fetchPost(postId) {
  return request(`/api/posts/${postId}`);
}

export function createPost(payload) {
  return request('/api/posts', { method: 'POST', body: JSON.stringify(payload) });
}

export function updatePost(postId, payload) {
  return request(`/api/posts/${postId}`, { method: 'PATCH', body: JSON.stringify(payload) });
}

export function deletePost(postId, password) {
  return request(`/api/posts/${postId}`, {
    method: 'DELETE',
    body: JSON.stringify({ password }),
  });
}
