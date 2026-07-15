<template>
  <section class="form-page">
    <router-link to="/community">← 게시판으로</router-link>
    <h2 class="page-title">{{ editing ? '게시글 수정' : '새 게시글 작성' }}</h2>
    <form class="post-form" @submit.prevent="submitPost">
      <label for="post-title">제목</label>
      <input id="post-title" v-model="form.title" maxlength="120" required />
      <label for="post-content">내용</label>
      <textarea id="post-content" v-model="form.content" rows="12" maxlength="10000" required />
      <label for="post-password">수정·삭제 비밀번호</label>
      <input id="post-password" v-model="form.password" type="password" minlength="4" maxlength="100" required />
      <p class="form-help">비밀번호는 수정과 삭제에 필요하며 다시 확인할 수 없습니다.</p>
      <p v-if="error" class="form-error" role="alert">{{ error }}</p>
      <button class="btn-primary" type="submit" :disabled="saving">{{ saving ? '저장 중' : '저장' }}</button>
    </form>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { createPost, fetchPost, updatePost } from '../api/posts';

const route = useRoute();
const router = useRouter();
const editing = computed(() => Boolean(route.params.postId));
const form = reactive({ title: '', content: '', password: '' });
const saving = ref(false);
const error = ref('');

onMounted(async () => {
  if (!editing.value) return;
  try {
    const post = await fetchPost(route.params.postId);
    form.title = post.title;
    form.content = post.content;
  } catch (err) {
    error.value = err.message;
  }
});

const submitPost = async () => {
  saving.value = true;
  error.value = '';
  try {
    const payload = { title: form.title, content: form.content, password: form.password };
    const post = editing.value
      ? await updatePost(route.params.postId, payload)
      : await createPost({ ...payload, region_id: 1 });
    await router.push(`/community/${post.post_id}`);
  } catch (err) {
    error.value = err.status === 403 ? '비밀번호가 일치하지 않습니다.' : err.message;
  } finally {
    saving.value = false;
  }
};
</script>
