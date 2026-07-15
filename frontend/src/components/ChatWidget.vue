<template>
  <div class="chat-widget">
    <button
      v-if="!open"
      class="chatbot-floating"
      type="button"
      aria-label="챗봇 열기"
      @click="open = true"
    >💬</button>

    <section v-else class="chat-panel" role="dialog" aria-modal="true" aria-label="지역 정보 챗봇">
      <header class="chat-header">
        <div>
          <strong>LocalHub 챗봇</strong>
          <small>제공 데이터 기반으로 답변합니다</small>
        </div>
        <button type="button" aria-label="챗봇 닫기" @click="open = false">×</button>
      </header>

      <div ref="messageLog" class="chat-messages" role="log" aria-live="polite">
        <p v-if="messages.length === 0" class="chat-empty">서울 축제나 주변 관광지를 물어보세요.</p>
        <article v-for="message in messages" :key="message.id" class="chat-message" :class="message.role">
          <p>{{ message.content }}</p>
          <ul v-if="message.sources?.length" class="chat-sources">
            <li v-for="source in message.sources" :key="`${source.type}-${source.id}`">
              {{ source.title }}<span v-if="source.distance_km"> · {{ source.distance_km.toFixed(1) }}km</span>
            </li>
          </ul>
        </article>
      </div>

      <form class="chat-composer" @submit.prevent="submitMessage">
        <label class="sr-only" for="chat-question">질문</label>
        <textarea
          id="chat-question"
          v-model="question"
          rows="2"
          maxlength="500"
          placeholder="서울 축제를 추천해줘"
          :disabled="sending"
          @keydown.enter.exact.prevent="submitMessage"
        />
        <button class="btn-primary" type="submit" :disabled="sending || !question.trim()">
          {{ sending ? '답변 중' : '전송' }}
        </button>
      </form>
    </section>
  </div>
</template>

<script setup>
import { nextTick, ref, watch } from 'vue';
import { sendChatMessage } from '../api/chat';

const STORAGE_KEY = 'localhub-chat-history';
const open = ref(false);
const question = ref('');
const sending = ref(false);
const messageLog = ref(null);
const savedMessages = sessionStorage.getItem(STORAGE_KEY);
const messages = ref(savedMessages ? JSON.parse(savedMessages) : []);

watch(messages, (value) => {
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(value.slice(-20)));
}, { deep: true });

const scrollToLatest = async () => {
  await nextTick();
  if (messageLog.value) messageLog.value.scrollTop = messageLog.value.scrollHeight;
};

const submitMessage = async () => {
  const content = question.value.trim();
  if (!content || sending.value) return;

  messages.value.push({ id: crypto.randomUUID(), role: 'user', content });
  question.value = '';
  sending.value = true;
  await scrollToLatest();

  try {
    const history = messages.value.slice(-7, -1).map(({ role, content: text }) => ({ role, content: text }));
    const response = await sendChatMessage({ question: content, history });
    messages.value.push({
      id: crypto.randomUUID(),
      role: 'assistant',
      content: response.answer,
      sources: response.sources || [],
    });
  } catch (error) {
    const content = error.status === 503
      ? '챗봇 설정을 확인해 주세요. 서버에 OpenAI API 키가 필요합니다.'
      : error.message;
    messages.value.push({ id: crypto.randomUUID(), role: 'assistant', content, error: true });
  } finally {
    sending.value = false;
    await scrollToLatest();
  }
};
</script>
