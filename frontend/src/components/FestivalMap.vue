<template>
  <div class="festival-map">
    <h3>지도 영역</h3>
    <p>축제 위치와 주변 장소를 표시할 영역입니다.</p>
  </div>
</template>

<script setup>
defineProps({ festival: Object, nearbyPlaces: Array });
</script>
