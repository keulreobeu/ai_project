import test from 'node:test';
import assert from 'node:assert/strict';
import { normalizeFestivalPayload } from '../src/utils/festivalResponse.js';

test('handles paginated payloads', () => {
  const result = normalizeFestivalPayload({
    items: [{ id: 1, title: 'A' }],
    page: 2,
    limit: 10,
    total_count: 1,
    total_pages: 1,
  });

  assert.equal(result.items.length, 1);
  assert.equal(result.page, 2);
  assert.equal(result.totalPages, 1);
});

test('handles legacy array payloads', () => {
  const result = normalizeFestivalPayload([
    { id: 1, title: 'A' },
    { id: 2, title: 'B' },
  ], 5);

  assert.equal(result.items.length, 2);
  assert.equal(result.page, 5);
  assert.equal(result.totalPages, 1);
});
