<template>
  <section>
    <router-link to="/">← 목록으로 돌아가기</router-link>
    <div v-if="loading" class="state-card">상세 정보를 불러오는 중입니다...</div>
    <div v-else-if="error" class="state-card error">상세 정보를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.</div>
    <div v-else-if="!festival.title" class="state-card">선택하신 축제 정보를 찾을 수 없습니다.</div>
    <div v-else class="detail-layout">
      <div class="map-box">
        <div class="map-content">
          <img v-if="festival.image_url || festival.thumbnail_url" class="detail-image" :src="festival.image_url || festival.thumbnail_url" :alt="festival.title" @error="onImageError" />
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
import { ref, watch, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import FestivalMap from '../components/FestivalMap.vue';
import MapPreview from '../components/MapPreview.vue';
import { fetchFestival, fetchNearbyPlaces } from '../api/festivals';

const props = defineProps({ festivalId: String });
const route = useRoute();
const festival = ref({ title: '', address: '' });
const nearbyPlaces = ref([]);
const loading = ref(false);
const error = ref(false);

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

const loadFestivalDetail = async () => {
  const id = props.festivalId || route.params.festivalId;
  if (!id) return;
  loading.value = true;
  error.value = false;
  try {
    const [festivalResult, nearbyResult] = await Promise.allSettled([
      fetchFestival(id),
      fetchNearbyPlaces(id)
    ]);
    if (festivalResult.status === 'rejected') {
      throw festivalResult.reason;
    }
    festival.value = festivalResult.value;
    const nearbyPayload = nearbyResult.status === 'fulfilled' ? nearbyResult.value : [];
    nearbyPlaces.value = Array.isArray(nearbyPayload) ? nearbyPayload : [];
  } catch (err) {
    error.value = true;
    festival.value = { title: '', address: '' };
    nearbyPlaces.value = [];
  } finally {
    loading.value = false;
  }
};

const onImageError = (event) => {
  event.target.style.display = 'none';
};

onMounted(loadFestivalDetail);
watch(() => route.params.festivalId, loadFestivalDetail);
</script>
