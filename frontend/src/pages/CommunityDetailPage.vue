<template>
  <section>
    <router-link to="/community">← 게시판으로</router-link>
    <div v-if="loading" class="state-card" role="status">게시글을 불러오는 중입니다...</div>
    <div v-else-if="error" class="state-card error" role="alert">{{ error }}</div>
    <article v-else-if="post" class="post-detail">
      <header>
        <h2>{{ post.title }}</h2>
        <time :datetime="post.created_at">{{ formatDate(post.created_at) }}</time>
      </header>
      <p>{{ post.content }}</p>
      <div class="post-actions">
        <router-link class="btn-secondary" :to="`/community/${post.post_id}/edit`">수정</router-link>
        <button class="btn-danger" type="button" @click="showDelete = !showDelete">삭제</button>
      </div>
      <form v-if="showDelete" class="password-panel" @submit.prevent="removePost">
        <label for="delete-password">작성 시 등록한 비밀번호</label>
        <input id="delete-password" v-model="password" type="password" minlength="4" required />
        <button class="btn-danger" type="submit" :disabled="deleting">삭제 확인</button>
      </form>
    </article>
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { deletePost, fetchPost } from '../api/posts';

const route = useRoute();
const router = useRouter();
const post = ref(null);
const loading = ref(false);
const error = ref('');
const showDelete = ref(false);
const password = ref('');
const deleting = ref(false);
const formatDate = (value) => new Intl.DateTimeFormat('ko-KR', { dateStyle: 'long', timeStyle: 'short' }).format(new Date(value));

const loadPost = async () => {
  loading.value = true;
  try {
    post.value = await fetchPost(route.params.postId);
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
};

const removePost = async () => {
  deleting.value = true;
  error.value = '';
  try {
    await deletePost(post.value.post_id, password.value);
    await router.replace('/community');
  } catch (err) {
    error.value = err.status === 403 ? '비밀번호가 일치하지 않습니다.' : err.message;
  } finally {
    deleting.value = false;
  }
};

onMounted(loadPost);
</script>
