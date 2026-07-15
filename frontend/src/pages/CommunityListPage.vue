<template>
  <section>
    <div class="page-heading-row">
      <div>
        <h2 class="page-title">익명 커뮤니티</h2>
        <p>서울 지역 정보와 여행 경험을 자유롭게 공유해 보세요.</p>
      </div>
      <router-link class="btn-primary" to="/community/new">글쓰기</router-link>
    </div>

    <form class="search-bar" @submit.prevent="loadPosts(1)">
      <label class="sr-only" for="post-search">게시글 검색</label>
      <input id="post-search" v-model="keyword" placeholder="제목 또는 내용을 검색하세요" />
      <button class="btn-primary" type="submit">검색</button>
    </form>

    <div v-if="loading" class="state-card" role="status">게시글을 불러오는 중입니다...</div>
    <div v-else-if="error" class="state-card error" role="alert">{{ error }}</div>
    <div v-else-if="posts.length === 0" class="state-card">첫 게시글을 작성해 보세요.</div>
    <div v-else class="post-list">
      <router-link v-for="post in posts" :key="post.post_id" class="post-row" :to="`/community/${post.post_id}`">
        <div>
          <h3>{{ post.title }}</h3>
          <p>{{ post.content }}</p>
        </div>
        <time :datetime="post.created_at">{{ formatDate(post.created_at) }}</time>
      </router-link>
    </div>

    <div v-if="totalPages > 1" class="pagination">
      <button :disabled="page === 1" @click="loadPosts(page - 1)">이전</button>
      <span>{{ page }} / {{ totalPages }}</span>
      <button :disabled="page === totalPages" @click="loadPosts(page + 1)">다음</button>
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import { fetchPosts } from '../api/posts';

const posts = ref([]);
const keyword = ref('');
const page = ref(1);
const totalPages = ref(0);
const loading = ref(false);
const error = ref('');

const formatDate = (value) => new Intl.DateTimeFormat('ko-KR', { dateStyle: 'medium' }).format(new Date(value));

const loadPosts = async (targetPage = 1) => {
  loading.value = true;
  error.value = '';
  try {
    const payload = await fetchPosts({ page: targetPage, q: keyword.value });
    posts.value = payload.items;
    page.value = payload.page;
    totalPages.value = payload.total_pages;
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
};

onMounted(() => loadPosts());
</script>
