// content_type_id: 12=관광지, 14=문화시설, 28=레포츠, 32=숙박, 38=쇼핑 (backend/app/services.py CATEGORY_LABEL_MAP과 동일 매핑)
export const CATEGORY_META = {
  12: { label: '관광지', color: 'var(--color-primary)' },
  14: { label: '문화시설', color: '#6366f1' },
  28: { label: '레포츠', color: 'var(--color-accent)' },
  32: { label: '숙박', color: '#f59e0b' },
  38: { label: '쇼핑', color: 'var(--color-secondary)' },
};

export const getCategoryMeta = (category) => CATEGORY_META[category] || { label: '추천', color: '#64748b' };

export const OSM_TILE_URL = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
export const OSM_ATTRIBUTION =
  '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors';

const escapeHtml = (value) =>
  String(value ?? '').replace(/[&<>"']/g, (char) => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;',
  })[char]);

// divIcon의 크기는 콘텐츠(제목 길이)에 따라 달라지므로 iconSize를 [0,0]으로 두고,
// 내부 div의 translate(-50%, -100%)로 "핀 끝(=좌표 지점)"을 정확히 앵커에 맞춘다.
export function createFestivalIcon(L, title) {
  const label = escapeHtml(title || '축제');
  return L.divIcon({
    className: 'map-festival-icon',
    html: `
      <div style="position:relative;transform:translate(-50%,-100%);display:flex;flex-direction:column;align-items:center;pointer-events:none;">
        <span style="background:#fff;color:var(--color-text);font-weight:700;font-size:12px;padding:6px 10px;border-radius:999px;box-shadow:0 6px 16px rgba(15,23,42,0.18);margin-bottom:6px;white-space:nowrap;max-width:180px;overflow:hidden;text-overflow:ellipsis;">${label}</span>
        <span style="width:18px;height:18px;border-radius:50%;background:var(--color-secondary);border:3px solid #fff;box-shadow:0 6px 14px rgba(255,107,53,0.45);display:block;"></span>
      </div>
    `,
    iconSize: [0, 0],
    iconAnchor: [0, 0],
  });
}

export function createPlaceIcon(L, place) {
  const meta = getCategoryMeta(place?.category);
  const label = escapeHtml(meta.label);
  return L.divIcon({
    className: 'map-place-icon',
    html: `<div style="position:relative;transform:translate(-50%,-100%);display:inline-flex;align-items:center;background:${meta.color};color:#fff;font-weight:700;font-size:11px;padding:5px 9px;border-radius:999px;box-shadow:0 4px 10px rgba(15,23,42,0.2);white-space:nowrap;">${label}</div>`,
    iconSize: [0, 0],
    iconAnchor: [0, 0],
  });
}
