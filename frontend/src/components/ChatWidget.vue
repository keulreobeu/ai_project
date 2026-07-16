<template>
  <div class="chat-widget" :style="{ '--chat-bottom-offset': `${footerOffset}px` }">
    <button class="chatbot-floating" aria-label="챗봇 열기" @click="open = !open">💬</button>
    <div v-if="open" class="chat-panel">
      <div class="chat-header">
        <span>축제 여행 챗봇</span>
        <button class="chat-close" aria-label="챗봇 닫기" @click="open = false">✕</button>
      </div>

      <div class="chat-messages" ref="messagesEl">
        <template v-for="(msg, idx) in messages" :key="idx">
          <div :class="['chat-bubble', msg.role === 'user' ? 'chat-bubble-user' : 'chat-bubble-bot']">
            {{ msg.content }}
          </div>

          <!-- 1단계 응답: 축제 후보를 칩으로 노출 -->
          <div v-if="msg.festivalOptions && msg.festivalOptions.length" class="chat-chip-row">
            <button
              v-for="f in msg.festivalOptions"
              :key="f.id"
              class="chat-chip"
              type="button"
              @click="selectFestival(f)"
            >{{ f.title }}</button>
          </div>

          <!-- 2단계: 카테고리 follow-up 칩 -->
          <div v-if="msg.categoryPrompt" class="chat-chip-row">
            <button
              v-for="c in categoryOptions"
              :key="c.value"
              class="chat-chip"
              type="button"
              @click="pickCategory(c)"
            >{{ c.label }}</button>
          </div>

          <!-- 3단계 응답: 실제 거리순 정렬 리스트(LLM 문장과 별개로 데이터 그대로 렌더링) -->
          <div v-if="msg.nearbyResults && msg.nearbyResults.length" class="chat-nearby-list">
            <div v-for="p in msg.nearbyResults" :key="p.id" class="chat-nearby-item">
              <strong>{{ p.title }}</strong>
              <span>{{ formatDistance(p.distance_km) }} · {{ p.address || '주소 정보 없음' }}</span>
            </div>
          </div>
        </template>

        <div v-if="loading" class="chat-bubble chat-bubble-bot chat-loading">
          <span></span><span></span><span></span>
        </div>
      </div>

      <form class="chat-input-row" @submit.prevent="sendFreeText">
        <input
          v-model="draft"
          placeholder="예: 강남 근처 가족이랑 갈만한 축제"
          :disabled="loading"
        />
        <button class="btn-primary" type="submit" :disabled="loading || !draft.trim()">전송</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, onBeforeUnmount } from 'vue';

/**
 * @typedef {Object} ChatSource
 * @property {number} id
 * @property {string} title
 * @property {string|null} address
 * @property {string|null} tel
 * @property {number|null} category
 * @property {number|null} distance_km
 */

/**
 * @typedef {Object} ChatMessageEntry
 * @property {'user'|'assistant'} role
 * @property {string} content
 * @property {ChatSource[]} [festivalOptions]
 * @property {boolean} [categoryPrompt]
 * @property {ChatSource[]} [nearbyResults]
 */

/** @type {import('vue').Ref<boolean>} */
const open = ref(false);
/** @type {import('vue').Ref<string>} */
const draft = ref('');
/** @type {import('vue').Ref<boolean>} */
const loading = ref(false);
/** @type {import('vue').Ref<HTMLElement|null>} */
const messagesEl = ref(null);
const footerOffset = ref(28);

const updateFooterOffset = () => {
  const footer = document.querySelector('.site-footer');
  if (!footer) {
    footerOffset.value = 28;
    return;
  }

  const visibleFooterHeight = Math.max(0, window.innerHeight - footer.getBoundingClientRect().top);
  footerOffset.value = visibleFooterHeight > 0 ? visibleFooterHeight + 28 : 28;
};

onMounted(() => {
  updateFooterOffset();
  window.addEventListener('scroll', updateFooterOffset, { passive: true });
  window.addEventListener('resize', updateFooterOffset);
});

onBeforeUnmount(() => {
  window.removeEventListener('scroll', updateFooterOffset);
  window.removeEventListener('resize', updateFooterOffset);
});

/** @type {import('vue').Ref<ChatMessageEntry[]>} */
const messages = ref([
  {
    role: 'assistant',
    content:
      '안녕하세요! 관심 있는 축제를 말씀해주세요. 지역이나 누구와 갈지도 함께 말씀해주시면 더 잘 골라드려요. (예: "강남 근처 가족이랑 갈만한 축제 추천해줘")',
  },
]);

/** @type {import('vue').Ref<{id:number,title:string}|null>} */
const selectedFestival = ref(null);

const categoryOptions = [
  { label: '관광지', value: '관광지' },
  { label: '문화시설', value: '문화시설' },
  { label: '레포츠', value: '레포츠' },
  { label: '숙박', value: '숙박' },
  { label: '쇼핑', value: '쇼핑' },
];

/** @param {number|null|undefined} km */
const formatDistance = (km) => (typeof km === 'number' ? `${km.toFixed(1)}km` : '거리 정보 없음');

const scrollToBottom = async () => {
  await nextTick();
  if (messagesEl.value) {
    messagesEl.value.scrollTop = messagesEl.value.scrollHeight;
  }
};

/**
 * @param {{ question: string, festival_id?: number, category?: string }} payload
 * @returns {Promise<Response>}
 */
const callChatApi = async (payload) => {
  const history = messages.value.map(({ role, content }) => ({ role, content }));
  return fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ...payload, history }),
  });
};

// 1단계: 자유 텍스트 → 축제 후보 탐색
const sendFreeText = async () => {
  const question = draft.value.trim();
  if (!question) return;
  messages.value.push({ role: 'user', content: question });
  draft.value = '';
  loading.value = true;
  scrollToBottom();
  try {
    const res = await callChatApi({ question });
    const data = await res.json();
    messages.value.push({
      role: 'assistant',
      content: res.ok ? data.answer : '죄송해요, 답변을 가져오지 못했어요.',
      festivalOptions: res.ok ? data.sources : [],
    });
  } catch (err) {
    messages.value.push({ role: 'assistant', content: '네트워크 오류가 발생했어요.' });
  } finally {
    loading.value = false;
    scrollToBottom();
  }
};

// 2단계: 축제 선택 → 카테고리 follow-up (백엔드 호출 없이 즉시 안내)
/** @param {{id:number,title:string}} festival */
const selectFestival = (festival) => {
  selectedFestival.value = festival;
  messages.value.push({ role: 'user', content: `"${festival.title}" 축제를 선택했어요.` });
  messages.value.push({
    role: 'assistant',
    content: `좋아요! "${festival.title}" 주변에 또 어떤 시설이 궁금하세요?`,
    categoryPrompt: true,
  });
  scrollToBottom();
};

// 3단계: 카테고리 선택 → festival_id 앵커 기준 거리순 추천
/** @param {{label:string,value:string}} category */
const pickCategory = async (category) => {
  if (!selectedFestival.value) return;
  messages.value.push({ role: 'user', content: `${category.label} 추천해줘` });
  loading.value = true;
  scrollToBottom();
  try {
    const res = await callChatApi({
      question: `${selectedFestival.value.title} 주변 ${category.label} 추천해줘`,
      festival_id: selectedFestival.value.id,
      category: category.value,
    });
    const data = await res.json();
    messages.value.push({
      role: 'assistant',
      content: res.ok ? data.answer : '죄송해요, 답변을 가져오지 못했어요.',
      nearbyResults: res.ok ? data.sources : [],
      categoryPrompt: res.ok, // 같은 축제로 다른 카테고리를 이어서 물어볼 수 있도록 칩을 다시 노출
    });
  } catch (err) {
    messages.value.push({ role: 'assistant', content: '네트워크 오류가 발생했어요.' });
  } finally {
    loading.value = false;
    scrollToBottom();
  }
};
</script>
