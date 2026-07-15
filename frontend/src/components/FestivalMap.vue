<template>
  <div class="festival-map">
    <div ref="mapContainer" class="festival-map-canvas"></div>
    <p v-if="!hasCoordinates" class="festival-map-hint">
      이 축제는 좌표 정보가 없어 대략적인 위치만 표시됩니다.
    </p>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { createFestivalIcon, createPlaceIcon, OSM_TILE_URL, OSM_ATTRIBUTION } from '../utils/mapMarkers';

const props = defineProps({
  festival: Object,
  nearbyPlaces: Array,
  radiusKm: { type: Number, default: 3 },
});

const DEFAULT_CENTER = [37.5665, 126.978]; // 좌표 정보가 없을 때의 서울시청 기준 대체 중심점

const mapContainer = ref(null);
const hasCoordinates = computed(
  () => Number.isFinite(props.festival?.latitude) && Number.isFinite(props.festival?.longitude)
);

let map = null;
let markers = [];

const zoomForRadius = (radiusKm) => {
  if (radiusKm <= 0.1) return 17;
  if (radiusKm <= 0.5) return 15;
  if (radiusKm <= 1) return 14;
  if (radiusKm <= 3) return 13;
  return 12;
};

const createPlaceTooltip = (place) => {
  const content = document.createElement('div');
  content.className = 'festival-place-tooltip-content';

  const title = document.createElement('strong');
  title.textContent = place.title || '장소 정보';
  content.appendChild(title);

  const address = document.createElement('span');
  address.textContent = place.address || '주소 정보 없음';
  content.appendChild(address);

  if (Number.isFinite(place.distance_km)) {
    const distance = document.createElement('small');
    distance.textContent = `축제에서 ${place.distance_km.toFixed(1)}km`;
    content.appendChild(distance);
  }

  return content;
};

const clearMarkers = () => {
  markers.forEach((marker) => marker.remove());
  markers = [];
};

const renderMarkers = () => {
  clearMarkers();

  if (hasCoordinates.value) {
    const rangeCircle = L.circle([props.festival.latitude, props.festival.longitude], {
      radius: props.radiusKm * 1000,
      color: '#0284c7',
      fillColor: '#38bdf8',
      fillOpacity: 0.08,
      weight: 2,
    }).addTo(map);
    markers.push(rangeCircle);

    const festivalMarker = L.marker([props.festival.latitude, props.festival.longitude], {
      icon: createFestivalIcon(L, props.festival?.title),
    }).addTo(map);
    markers.push(festivalMarker);
  }

  (props.nearbyPlaces || [])
    .filter((place) => Number.isFinite(place.latitude) && Number.isFinite(place.longitude))
    .forEach((place) => {
      const marker = L.marker([place.latitude, place.longitude], { icon: createPlaceIcon(L, place) })
        .addTo(map)
        .bindTooltip(createPlaceTooltip(place), {
          className: 'festival-place-tooltip',
          direction: 'top',
          offset: [0, -10],
          opacity: 0.96,
        });
      markers.push(marker);
    });
};

const renderMap = () => {
  if (!mapContainer.value) return;
  const center = hasCoordinates.value ? [props.festival.latitude, props.festival.longitude] : DEFAULT_CENTER;

  if (!map) {
    map = L.map(mapContainer.value).setView(center, zoomForRadius(props.radiusKm));
    L.tileLayer(OSM_TILE_URL, { attribution: OSM_ATTRIBUTION, maxZoom: 19 }).addTo(map);
  } else {
    map.setView(center, zoomForRadius(props.radiusKm));
  }

  renderMarkers();
};

onMounted(() => {
  nextTick(renderMap);
});

watch(
  () => [
    props.festival?.id,
    props.festival?.latitude,
    props.festival?.longitude,
    props.nearbyPlaces,
    props.radiusKm,
  ],
  () => nextTick(renderMap),
  { deep: true }
);

onBeforeUnmount(() => {
  clearMarkers();
  if (map) {
    map.remove();
    map = null;
  }
});
</script>

<style scoped>
.festival-map {
  margin-top: 16px;
}

.festival-map-canvas {
  width: 100%;
  height: 420px;
  border-radius: 20px;
  overflow: hidden;
  border: 1px solid var(--color-border);
}

.festival-map-hint {
  margin: 10px 0 0;
  font-size: 12px;
  color: var(--color-muted);
}

:global(.festival-place-tooltip-content) { display: grid; gap: 4px; min-width: 160px; }
:global(.festival-place-tooltip-content strong) { color: #0f172a; font-size: 13px; }
:global(.festival-place-tooltip-content span) { color: #475569; font-size: 11px; white-space: normal; }
:global(.festival-place-tooltip-content small) { color: #0284c7; font-size: 11px; font-weight: 800; }
</style>
