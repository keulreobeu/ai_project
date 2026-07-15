<template>
  <article class="festival-card">
    <div class="festival-image-wrap">
      <img v-if="festival.image_url || festival.thumbnail_url" :src="festival.image_url || festival.thumbnail_url" :alt="festival.title" @error="onImageError" />
      <div v-else class="festival-image-placeholder">이미지 없음</div>
    </div>
    <div class="festival-card-content">
      <span class="tag">#축제</span>
      <h3>{{ festival.title }}</h3>
      <p>{{ festival.address }}</p>
      <router-link class="btn-primary" :to="`/festivals/${festival.id}`">자세히 보기</router-link>
    </div>
  </article>
</template>

<script setup>
defineProps({ festival: Object });
const onImageError = (event) => {
  event.target.style.display = 'none';
};
</script>
