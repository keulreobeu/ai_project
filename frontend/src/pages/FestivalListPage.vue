<template>
  <section>
    <h2 class="page-title">서울 축제/행사</h2>
    <p>이번 주 추천 축제와 공연 정보를 한눈에 확인해보세요.</p>
    <div class="search-bar">
      <input v-model="keyword" placeholder="축제명을 검색하세요" @keyup.enter="loadFestivals" />
      <button class="btn-primary" @click="loadFestivals">검색</button>
    </div>
    <p v-if="loading">축제 정보를 불러오는 중입니다...</p>
    <p v-else-if="error">데이터를 불러오지 못했습니다.</p>
    <div v-else class="festival-grid">
      <FestivalCard v-for="festival in festivals" :key="festival.id" :festival="festival" />
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import FestivalCard from '../components/FestivalCard.vue';

const festivals = ref([]);
const keyword = ref('');
const loading = ref(false);
const error = ref(false);

const loadFestivals = async () => {
  loading.value = true;
  error.value = false;
  try {
    const response = await fetch(`/api/festivals?keyword=${encodeURIComponent(keyword.value)}`);
    festivals.value = await response.json();
  } catch (err) {
    error.value = true;
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  loadFestivals();
});
</script>
