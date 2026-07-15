import { request } from './http';


export function sendChatMessage(payload) {
  return request('/api/chat', { method: 'POST', body: JSON.stringify(payload) });
}
