<template>
  <article class="festival-card">
    <img v-if="festival.thumbnail_url" :src="festival.thumbnail_url" :alt="festival.title" />
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
</script>
