import { request } from './http';


export function fetchPosts({ page = 1, limit = 20, q = '' } = {}) {
  const params = new URLSearchParams({ page, limit });
  if (q) params.set('q', q);
  return request(`/api/community/posts?${params.toString()}`);
}

export function fetchPost(postId) {
  return request(`/api/community/posts/${postId}`);
}

export function createPost(payload) {
  return request('/api/community/posts', { method: 'POST', body: JSON.stringify(payload) });
}

export function updatePost(postId, payload) {
  return request(`/api/community/posts/${postId}`, { method: 'PUT', body: JSON.stringify(payload) });
}

export function verifyPostPassword(postId, password) {
  return request(`/api/community/posts/${postId}/verify-password`, {
    method: 'POST',
    body: JSON.stringify({ password }),
  });
}

export function deletePost(postId, password) {
  return request(`/api/community/posts/${postId}`, {
    method: 'DELETE',
    body: JSON.stringify({ password }),
  });
}
