<template>
  <div class="map-preview">
    <div class="map-pin" />
    <div class="map-label">{{ festival.title }}</div>
    <div v-for="place in nearbyPlaces.slice(0, 4)" :key="place.id" class="map-marker" :class="getCategoryClass(place.category)">
      {{ getCategoryLabel(place.category) }}
    </div>
  </div>
</template>

<script setup>
defineProps({ festival: Object, nearbyPlaces: Array });

const getCategoryLabel = (category) => {
  const map = { 12: '관광', 14: '문화', 28: '레포츠', 32: '숙박', 38: '쇼핑' };
  return map[category] || '추천';
};

const getCategoryClass = (category) => {
  const map = { 12: 'tour', 14: 'culture', 28: 'sports', 32: 'stay', 38: 'shop' };
  return map[category] || 'default';
};
</script>
