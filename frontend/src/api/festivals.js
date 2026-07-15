import { request } from './http';


export function fetchFestivals({ page, limit = 20, keyword = '' } = {}) {
  const params = new URLSearchParams();
  if (page) params.set('page', page);
  if (limit) params.set('limit', limit);
  if (keyword) params.set('keyword', keyword);
  const query = params.toString();
  return request(`/api/festivals${query ? `?${query}` : ''}`);
}

export function fetchFestival(festivalId) {
  return request(`/api/festivals/${festivalId}`);
}

export function fetchNearbyPlaces(festivalId) {
  return request(`/api/festivals/${festivalId}/nearby`);
}
