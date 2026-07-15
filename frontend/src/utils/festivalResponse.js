export function normalizeFestivalPayload(payload, fallbackPage = 1) {
  if (Array.isArray(payload)) {
    return {
      items: payload,
      page: fallbackPage,
      totalPages: 1,
    };
  }

  const items = Array.isArray(payload?.items) ? payload.items : [];
  const page = Number(payload?.page || fallbackPage || 1);
  const limit = Number(payload?.limit || 10);
  const totalCount = Number(payload?.total_count || items.length || 0);
  const totalPages = Number(payload?.total_pages || Math.max(1, Math.ceil(totalCount / limit)) || 1);

  return {
    items,
    page: Number.isFinite(page) ? page : fallbackPage,
    totalPages: Number.isFinite(totalPages) ? totalPages : 1,
  };
}
