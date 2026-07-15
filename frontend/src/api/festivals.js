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

export function fetchCalendarFestivals(year, month) {
  const params = new URLSearchParams({ year, month });
  return request(`/api/festivals/calendar?${params.toString()}`);
}

export function fetchNearbyPlaces(
  festivalId,
  { radiusKm = 3, limit = 10, allPlaces = false } = {},
) {
  const params = new URLSearchParams({ radius_km: radiusKm });
  if (allPlaces) {
    params.set('all_places', 'true');
  } else {
    params.set('limit', limit);
  }
  return request(`/api/festivals/${festivalId}/nearby?${params.toString()}`);
}
