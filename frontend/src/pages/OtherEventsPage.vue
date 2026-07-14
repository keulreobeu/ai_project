<template>
  <section>
    <router-link to="/">← 메인으로 돌아가기</router-link>
    <h2 class="page-title">다른 행사 더 보기</h2>
    <p>다음 페이지의 서울 행사들을 이어서 확인해보세요.</p>

    <div v-if="loading" class="state-card">다른 행사를 불러오는 중입니다...</div>
    <div v-else-if="error" class="state-card error">다른 행사를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.</div>
    <div v-else-if="events.length === 0" class="state-card">표시할 다른 행사가 없습니다.</div>
    <div v-else class="festival-grid">
      <FestivalCard v-for="festival in events" :key="festival.id" :festival="festival" badgeText="#다른 행사" />
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import FestivalCard from '../components/FestivalCard.vue';

const events = ref([]);
const loading = ref(false);
const error = ref(false);

const loadEvents = async () => {
  loading.value = true;
  error.value = false;
  try {
    const response = await fetch('/api/festivals?page=2&limit=20');
    if (!response.ok) {
      throw new Error('failed');
    }
    const payload = await response.json();
    events.value = payload.items || [];
  } catch (err) {
    error.value = true;
    events.value = [];
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  loadEvents();
});
</script>
