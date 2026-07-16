import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';


const detailSource = await readFile(
  new URL('../src/components/CommunityPostDetail.vue', import.meta.url),
  'utf8',
);
const pageSource = await readFile(
  new URL('../src/pages/CommunityPage.vue', import.meta.url),
  'utf8',
);
const apiSource = await readFile(new URL('../src/api/posts.js', import.meta.url), 'utf8');


test('password verification never targets localhost in the production component', () => {
  assert.doesNotMatch(detailSource, /127\.0\.0\.1:8001/);
  assert.match(detailSource, /verifyPostPassword\(this\.post\.post_id, enteredPassword\)/);
});


test('community deletion uses the shared JSON-body API contract', () => {
  assert.match(pageSource, /await deletePostRequest\(postId, password\)/);
  assert.doesNotMatch(pageSource, /\?password=/);
  assert.match(apiSource, /method: 'DELETE'/);
  assert.match(apiSource, /body: JSON\.stringify\(\{ password \}\)/);
});


test('password verification errors are visible in both confirmation dialogs', () => {
  assert.match(detailSource, /v-if="editError"/);
  assert.match(detailSource, /v-if="deleteError"/);
});
