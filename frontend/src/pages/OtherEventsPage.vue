<template>
  <section>
    <router-link to="/">← 축제 목록으로 돌아가기</router-link>
    <h2 class="page-title">행사 목록</h2>
    <p>서울에서 열리는 다양한 행사를 목록으로 확인해보세요.</p>

    <div class="toolbar">
      <input v-model="keyword" placeholder="행사명 또는 주소 검색" @keyup.enter="applyFilters" />
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
      <div class="event-list">
        <article v-for="festival in sortedEvents" :key="festival.id" class="event-item">
          <div class="event-thumb">
            <img v-if="festival.image_url || festival.thumbnail_url" :src="festival.image_url || festival.thumbnail_url" :alt="festival.title" @error="onImageError" />
            <div v-else class="festival-image-placeholder">이미지 없음</div>
          </div>
          <div class="event-body">
            <h3>{{ festival.title }}</h3>
            <p>{{ festival.address }}</p>
            <router-link class="event-detail-link" :to="`/festivals/${festival.id}`">자세히 보기</router-link>
          </div>
        </article>
      </div>

      <div class="pagination" v-if="totalPages > 1">
        <button type="button" aria-label="이전 페이지" :disabled="page === 1" @click="goToPage(page - 1)">‹</button>
        <button v-for="p in visiblePages" :key="p" :class="{ active: p === page }" @click="goToPage(p)">{{ p }}</button>
        <button type="button" aria-label="다음 페이지" :disabled="page === totalPages" @click="goToPage(page + 1)">›</button>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { normalizeFestivalPayload } from '../utils/festivalResponse';
import { fetchFestivals } from '../api/festivals';

const events = ref([]);
const loading = ref(false);
const error = ref(false);
const page = ref(1);
const totalPages = ref(1);
const keyword = ref('');
const sortOrder = ref('latest');
const pageSize = 20;
const MAX_VISIBLE_PAGE_BUTTONS = 5;

const visiblePages = computed(() => {
  const total = totalPages.value;
  const halfWindow = Math.floor(MAX_VISIBLE_PAGE_BUTTONS / 2);
  let start = Math.max(1, page.value - halfWindow);
  let end = Math.min(total, start + MAX_VISIBLE_PAGE_BUTTONS - 1);

  if (end - start + 1 < MAX_VISIBLE_PAGE_BUTTONS) {
    start = Math.max(1, end - MAX_VISIBLE_PAGE_BUTTONS + 1);
  }

  return Array.from({ length: end - start + 1 }, (_, index) => start + index);
});

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
    const payload = await fetchFestivals({ page: targetPage, limit: pageSize, keyword: keyword.value });
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

<style scoped>
.toolbar {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 140px auto;
  gap: 12px;
  margin: 20px 0 28px;
}

.toolbar input,
.toolbar select {
  min-height: 42px;
  padding: 10px 14px;
  border: 1px solid var(--color-border);
  border-radius: 10px;
  background: white;
  font: inherit;
}

.toolbar .btn-primary {
  min-height: 42px;
  margin: 0;
  border-radius: 10px;
  background: #a6a6a6;
  font-family: inherit;
}

.event-list {
  display: grid;
  gap: 16px;
}

.event-item {
  display: grid;
  grid-template-columns: 180px minmax(0, 1fr);
  height: 170px;
  overflow: hidden;
  border-radius: 20px;
  background: var(--color-card);
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.event-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 14px 32px rgba(15, 23, 42, 0.12);
}

.event-thumb,
.event-thumb img,
.event-thumb .festival-image-placeholder {
  width: 100%;
  height: 100%;
}

.event-thumb img { display: block; object-fit: cover; }
.event-thumb .festival-image-placeholder { display: grid; place-items: center; background: #f1f5f9; color: var(--color-muted); }

.event-body {
  display: flex;
  flex-direction: column;
  padding: 22px 24px;
  font-family: 'Pretendard', 'Noto Sans KR', sans-serif;
}

.event-body h3 {
  display: -webkit-box;
  overflow: hidden;
  margin: 0 0 10px;
  font-size: 20px;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.event-body p {
  display: -webkit-box;
  overflow: hidden;
  margin: 0;
  color: var(--color-muted);
  line-height: 1.6;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 1;
}

.event-detail-link {
  align-self: flex-end;
  margin-top: auto;
  padding-top: 16px;
  color: var(--color-muted);
  font-weight: 600;
}

@media (max-width: 700px) {
  .toolbar { grid-template-columns: 1fr; }
  .event-item { grid-template-columns: 110px minmax(0, 1fr); height: 160px; }
  .event-body { padding: 18px; }
}
</style>
