<template>
  <section>
    <h2 class="page-title">서울 축제/행사</h2>
    <p>이번 주 추천 축제와 공연 정보를 한눈에 확인해보세요.</p>
    <div class="search-bar">
      <input v-model="keyword" placeholder="축제명을 검색하세요" @keyup.enter="loadFestivals(1)" />
      <button class="btn-primary" @click="loadFestivals(1)">검색</button>
    </div>
    <div class="page-actions">
      <router-link class="btn-secondary" to="/events">다른 행사 더 보기</router-link>
    </div>
    <div v-if="loading" class="state-card">축제 정보를 불러오는 중입니다...</div>
    <div v-else-if="error" class="state-card error">데이터를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.</div>
    <div v-else-if="festivals.length === 0" class="state-card">검색 결과가 없습니다.</div>
    <div v-else>
      <div class="festival-grid">
        <FestivalCard v-for="festival in festivals" :key="festival.id" :festival="festival" />
      </div>
      <div class="pagination" v-if="totalPages > 1">
        <button :disabled="page === 1" @click="loadFestivals(page - 1)">이전</button>
        <button v-for="p in visiblePages" :key="p" :class="{ active: p === page }" @click="loadFestivals(p)">{{ p }}</button>
        <button :disabled="page === totalPages" @click="loadFestivals(page + 1)">다음</button>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import FestivalCard from '../components/FestivalCard.vue';

const festivals = ref([]);
const keyword = ref('');
const loading = ref(false);
const error = ref(false);
const page = ref(1);
const totalPages = ref(1);
const totalCount = ref(0);

const visiblePages = computed(() => {
  const pages = [];
  const start = Math.max(1, page.value - 2);
  const end = Math.min(totalPages.value, page.value + 2);
  for (let p = start; p <= end; p += 1) {
    pages.push(p);
  }
  return pages;
});

const loadFestivals = async (targetPage = 1) => {
  loading.value = true;
  error.value = false;
  page.value = targetPage;
  try {
    const response = await fetch(`/api/festivals?page=${targetPage}&limit=20&keyword=${encodeURIComponent(keyword.value)}`);
    if (!response.ok) {
      throw new Error('failed');
    }
    const payload = await response.json();
    if (Array.isArray(payload)) {
      festivals.value = payload;
      totalPages.value = 1;
      totalCount.value = payload.length;
    } else {
      festivals.value = payload.items || [];
      totalPages.value = payload.total_pages || 1;
      totalCount.value = payload.total_count || 0;
    }
  } catch (err) {
    error.value = true;
    festivals.value = [];
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  loadFestivals(1);
});
</script>
