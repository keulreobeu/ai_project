<template>
  <section class="festival-detail-page">
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
          <div class="recommendation-toolbar">
            <div>
              <h3>주변 추천장소 목록</h3>
              <span>축제에서 가까운 3km 이내 장소</span>
            </div>
            <label>
              표시 개수
              <select v-model.number="recommendationLimit" @change="reloadRecommendedPlaces">
                <option v-for="limit in recommendationLimitOptions" :key="limit" :value="limit">
                  {{ limit }}개
                </option>
              </select>
            </label>
          </div>
          <p v-if="recommendationLoading" class="nearby-state" role="status">추천 장소를 불러오는 중입니다...</p>
          <p v-else-if="recommendedPlaces.length === 0" class="nearby-state">3km 이내 추천 장소가 없습니다.</p>
          <div v-else class="nearby-list">
            <div v-for="place in recommendedPlaces" :key="place.id" class="nearby-item">
              <div>
                <strong>{{ place.title }}</strong>
                <small>{{ place.address || '주소 정보 없음' }}</small>
              </div>
              <div class="nearby-meta">
                <span class="tag">{{ getCategoryLabel(place.category) }}</span>
                <small v-if="Number.isFinite(place.distance_km)">{{ place.distance_km.toFixed(1) }}km</small>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="info-panel">
        <h3>축제 정보</h3>
        <p>{{ festival.address }}</p>
        <p>상세 페이지에서는 축제 소개, 지도, 주변 관광지, 숙박, 레포츠, 문화시설, 쇼핑 정보를 함께 보여줄 예정입니다.</p>
        <div class="range-control">
          <div class="range-control-heading">
            <label for="nearby-radius">지도 주변 범위</label>
            <output for="nearby-radius">{{ selectedRadiusKm }}km</output>
          </div>
          <input
            id="nearby-radius"
            v-model.number="radiusStep"
            type="range"
            min="0"
            max="4"
            step="1"
            :aria-valuetext="`${selectedRadiusKm}km`"
            @change="reloadMapPlaces"
          />
          <div class="range-labels" aria-hidden="true">
            <span v-for="radius in radiusOptions" :key="radius">{{ radius }}km</span>
          </div>
          <small v-if="mapLoading" role="status">선택한 범위의 주변 장소를 불러오는 중입니다...</small>
        </div>
        <FestivalMap
          :festival="festival"
          :nearbyPlaces="mapPlaces"
          :radius-km="selectedRadiusKm"
        />
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, ref, watch, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import FestivalMap from '../components/FestivalMap.vue';
import { fetchFestival, fetchNearbyPlaces } from '../api/festivals';

const props = defineProps({ festivalId: String });
const route = useRoute();
const festival = ref({ title: '', address: '' });
const recommendedPlaces = ref([]);
const mapPlaces = ref([]);
const loading = ref(false);
const error = ref(false);
const recommendationLoading = ref(false);
const mapLoading = ref(false);
const recommendationLimitOptions = [10, 20, 30, 40, 50];
const recommendationLimit = ref(10);
const radiusOptions = [0.1, 0.5, 1, 3, 5];
const radiusStep = ref(1);
const selectedRadiusKm = computed(() => radiusOptions[radiusStep.value]);
let recommendationRequestSequence = 0;
let mapRequestSequence = 0;

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
  recommendationRequestSequence += 1;
  mapRequestSequence += 1;
  recommendationLoading.value = false;
  mapLoading.value = false;
  loading.value = true;
  error.value = false;
  try {
    const [festivalResult, recommendationResult, mapResult] = await Promise.allSettled([
      fetchFestival(id),
      fetchNearbyPlaces(id, { radiusKm: 3, limit: recommendationLimit.value }),
      fetchNearbyPlaces(id, { radiusKm: selectedRadiusKm.value, allPlaces: true }),
    ]);
    if (festivalResult.status === 'rejected') {
      throw festivalResult.reason;
    }
    festival.value = festivalResult.value;
    const recommendationPayload = recommendationResult.status === 'fulfilled' ? recommendationResult.value : [];
    const mapPayload = mapResult.status === 'fulfilled' ? mapResult.value : [];
    recommendedPlaces.value = Array.isArray(recommendationPayload) ? recommendationPayload : [];
    mapPlaces.value = Array.isArray(mapPayload) ? mapPayload : [];
  } catch (err) {
    error.value = true;
    festival.value = { title: '', address: '' };
    recommendedPlaces.value = [];
    mapPlaces.value = [];
  } finally {
    loading.value = false;
  }
};

const reloadRecommendedPlaces = async () => {
  const id = props.festivalId || route.params.festivalId;
  if (!id) return;

  const requestSequence = ++recommendationRequestSequence;
  recommendationLoading.value = true;
  try {
    const payload = await fetchNearbyPlaces(id, { radiusKm: 3, limit: recommendationLimit.value });
    if (requestSequence === recommendationRequestSequence) {
      recommendedPlaces.value = Array.isArray(payload) ? payload : [];
    }
  } catch (err) {
    if (requestSequence === recommendationRequestSequence) recommendedPlaces.value = [];
  } finally {
    if (requestSequence === recommendationRequestSequence) recommendationLoading.value = false;
  }
};

const reloadMapPlaces = async () => {
  const id = props.festivalId || route.params.festivalId;
  if (!id) return;

  const requestSequence = ++mapRequestSequence;
  mapLoading.value = true;
  try {
    const payload = await fetchNearbyPlaces(id, { radiusKm: selectedRadiusKm.value, allPlaces: true });
    if (requestSequence === mapRequestSequence) {
      mapPlaces.value = Array.isArray(payload) ? payload : [];
    }
  } catch (err) {
    if (requestSequence === mapRequestSequence) mapPlaces.value = [];
  } finally {
    if (requestSequence === mapRequestSequence) mapLoading.value = false;
  }
};

const onImageError = (event) => {
  event.target.style.display = 'none';
};

onMounted(loadFestivalDetail);
watch(() => route.params.festivalId, loadFestivalDetail);
</script>

<style scoped>
.festival-detail-page {
  width: min(1500px, calc(100vw - 32px));
  margin-left: 50%;
  transform: translateX(-50%);
}

.detail-layout {
  grid-template-columns: minmax(0, 1.8fr) minmax(300px, 1fr);
}

.detail-image {
  display: block;
  width: 100%;
  aspect-ratio: 3 / 1;
  object-fit: contain;
  object-position: center;
  border-radius: 20px;
  background: #f1f5f9;
}

.recommendation-toolbar {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  margin-top: 24px;
  padding-bottom: 14px;
  border-bottom: 1px solid var(--color-border);
}

.recommendation-toolbar h3 { margin: 0 0 4px; color: var(--color-text); }
.recommendation-toolbar span { font-size: 13px; }
.recommendation-toolbar label { display: grid; gap: 5px; font-size: 12px; font-weight: 700; }
.recommendation-toolbar select {
  min-width: 100px;
  padding: 8px 10px;
  border: 1px solid var(--color-border);
  border-radius: 10px;
  background: white;
}
.nearby-state { margin: 18px 0 0; color: var(--color-muted); }
.nearby-item > div:first-child { display: grid; gap: 3px; }
.nearby-item small { color: var(--color-muted); }
.nearby-meta { display: grid; justify-items: end; gap: 5px; flex: 0 0 auto; }

.range-control {
  margin-top: 20px;
  padding: 16px;
  border: 1px solid var(--color-border);
  border-radius: 16px;
  background: #f8fafc;
}

.range-control-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 10px;
}

.range-control-heading label { font-weight: 800; }
.range-control-heading output { color: var(--color-primary); font-weight: 900; }
.range-control input[type='range'] { width: 100%; accent-color: var(--color-primary); cursor: pointer; }
.range-labels { display: flex; justify-content: space-between; margin-top: 4px; color: var(--color-muted); font-size: 11px; }
.range-control small { display: block; margin-top: 10px; color: var(--color-muted); }

@media (max-width: 900px) {
  .festival-detail-page {
    width: 100%;
    margin-left: 0;
    transform: none;
  }

  .detail-layout {
    grid-template-columns: minmax(0, 1fr);
  }

  .recommendation-toolbar { align-items: flex-start; }
}
</style>
