<template>
  <section>
    <router-link to="/">← 목록으로 돌아가기</router-link>
    <div class="detail-layout">
      <div class="map-box">
        <div class="map-content">
          <h2>{{ festival.title }}</h2>
          <p>{{ festival.address }}</p>
          <p>지도에서 행사 위치와 주변 추천 장소를 확인할 수 있는 영역입니다.</p>
          <MapPreview :festival="festival" :nearbyPlaces="nearbyPlaces" />
          <div class="nearby-list">
            <div v-for="place in nearbyPlaces" :key="place.id" class="nearby-item">
              <strong>{{ place.title }}</strong>
              <span class="tag">{{ getCategoryLabel(place.category) }}</span>
            </div>
          </div>
        </div>
      </div>
      <div class="info-panel">
        <h3>축제 정보</h3>
        <p>{{ festival.address }}</p>
        <p>상세 페이지에서는 축제 소개, 지도, 주변 관광지, 숙박, 레포츠, 문화시설, 쇼핑 정보를 함께 보여줄 예정입니다.</p>
        <FestivalMap :festival="festival" :nearbyPlaces="nearbyPlaces" />
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import FestivalMap from '../components/FestivalMap.vue';
import MapPreview from '../components/MapPreview.vue';

const props = defineProps({ festivalId: String });
const route = useRoute();
const festival = ref({ title: '', address: '' });
const nearbyPlaces = ref([]);

const getCategoryLabel = (category) => {
  const map = {
    12: '관광지',
    14: '문화시설',
    28: '레포츠',
    32: '숙박',
    38: '쇼핑'
  };
  return map[category] || '추천장소';
};

onMounted(async () => {
  const id = props.festivalId || route.params.festivalId;
  const [festivalResponse, nearbyResponse] = await Promise.all([
    fetch(`/api/festivals/${id}`),
    fetch(`/api/festivals/${id}/nearby`)
  ]);
  festival.value = await festivalResponse.json();
  nearbyPlaces.value = await nearbyResponse.json();
});
</script>
