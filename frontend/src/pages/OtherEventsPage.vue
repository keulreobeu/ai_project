<template>
  <section>
    <router-link to="/">← 메인으로 돌아가기</router-link>
    <h2 class="page-title">커뮤니티/갤러리형 행사 목록</h2>
    <p>다음 페이지의 서울 행사들을 이어서 확인해보세요.</p>

    <div class="toolbar">
      <input v-model="keyword" placeholder="행사명 검색" @keyup.enter="applyFilters" />
      <select v-model="sortOrder">
        <option value="latest">최신순</option>
        <option value="title">제목순</option>
      </select>
      <button class="btn-primary" @click="applyFilters">검색</button>
    </div>

    <div v-if="loading" class="state-card">행사 목록을 불러오는 중입니다...</div>
    <div v-else-if="error" class="state-card error">행사 목록을 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.</div>
    <div v-else-if="events.length === 0" class="state-card">표시할 행사가 없습니다.</div>
    <div v-else>
      <div class="community-list">
        <article v-for="festival in sortedEvents" :key="festival.id" class="community-item">
          <div class="community-thumb">
            <img v-if="festival.image_url || festival.thumbnail_url" :src="festival.image_url || festival.thumbnail_url" :alt="festival.title" @error="onImageError" />
            <div v-else class="festival-image-placeholder">이미지 없음</div>
          </div>
          <div class="community-body">
            <div class="community-meta">
              <span class="tag">#행사</span>
              <span class="community-page">페이지 {{ page }}</span>
            </div>
            <h3>{{ festival.title }}</h3>
            <p>{{ festival.address }}</p>
            <router-link class="btn-primary" :to="`/festivals/${festival.id}`">자세히 보기</router-link>
          </div>
        </article>
      </div>

      <div class="pagination" v-if="totalPages > 1">
        <button :disabled="page === 1" @click="goToPage(1)">««</button>
        <button :disabled="page === 1" @click="goToPage(page - 1)">이전</button>
        <button v-for="p in visiblePages" :key="p" :class="{ active: p === page }" @click="goToPage(p)">{{ p }}</button>
        <button :disabled="page === totalPages" @click="goToPage(page + 1)">다음</button>
        <button :disabled="page === totalPages" @click="goToPage(totalPages)">»»</button>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { normalizeFestivalPayload } from '../utils/festivalResponse';

const events = ref([]);
const loading = ref(false);
const error = ref(false);
const page = ref(1);
const totalPages = ref(1);
const keyword = ref('');
const sortOrder = ref('latest');
const pageSize = 20;

const visiblePages = computed(() => Array.from({ length: totalPages.value }, (_, index) => index + 1));

const sortedEvents = computed(() => {
  const list = [...events.value];
  if (sortOrder.value === 'title') {
    return list.sort((a, b) => a.title.localeCompare(b.title, 'ko'));
  }
  return list;
});

const loadEvents = async (targetPage = 1) => {
  loading.value = true;
  error.value = false;
  page.value = targetPage;
  try {
    const response = await fetch(`/api/festivals?page=${targetPage}&limit=${pageSize}${keyword.value ? `&keyword=${encodeURIComponent(keyword.value)}` : ''}`);
    if (!response.ok) {
      throw new Error('failed');
    }
    const payload = await response.json();
    const normalized = normalizeFestivalPayload(payload, targetPage);
    events.value = normalized.items || [];
    totalPages.value = normalized.totalPages || 1;
    window.scrollTo({ top: 0, behavior: 'smooth' });
  } catch (err) {
    error.value = true;
    events.value = [];
  } finally {
    loading.value = false;
  }
};

const applyFilters = () => {
  loadEvents(1);
};

const goToPage = (targetPage) => {
  if (targetPage < 1 || targetPage > totalPages.value) return;
  loadEvents(targetPage);
};

const onImageError = (event) => {
  event.target.style.display = 'none';
};

onMounted(() => {
  loadEvents(1);
});
</script>
