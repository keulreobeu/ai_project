<template>
  <div ref="mapContainer" class="map-preview"></div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { createFestivalIcon, createPlaceIcon, OSM_TILE_URL, OSM_ATTRIBUTION } from '../utils/mapMarkers';

const props = defineProps({ festival: Object, nearbyPlaces: Array });

const DEFAULT_CENTER = [37.5665, 126.978]; // 좌표 정보가 없을 때의 서울시청 기준 대체 중심점

const mapContainer = ref(null);
const hasCoordinates = computed(
  () => Number.isFinite(props.festival?.latitude) && Number.isFinite(props.festival?.longitude)
);
const previewPlaces = computed(() => (props.nearbyPlaces || []).slice(0, 4));

let map = null;
let markers = [];

const clearMarkers = () => {
  markers.forEach((marker) => marker.remove());
  markers = [];
};

const renderMarkers = () => {
  clearMarkers();

  if (hasCoordinates.value) {
    const festivalMarker = L.marker([props.festival.latitude, props.festival.longitude], {
      icon: createFestivalIcon(L, props.festival?.title),
    }).addTo(map);
    markers.push(festivalMarker);
  }

  previewPlaces.value
    .filter((place) => Number.isFinite(place.latitude) && Number.isFinite(place.longitude))
    .forEach((place) => {
      const marker = L.marker([place.latitude, place.longitude], { icon: createPlaceIcon(L, place) })
        .addTo(map)
        .bindPopup(place.title || '');
      markers.push(marker);
    });
};

const renderMap = () => {
  if (!mapContainer.value) return;
  const center = hasCoordinates.value ? [props.festival.latitude, props.festival.longitude] : DEFAULT_CENTER;

  if (!map) {
    map = L.map(mapContainer.value, { zoomControl: false }).setView(center, 14);
    L.tileLayer(OSM_TILE_URL, { attribution: OSM_ATTRIBUTION, maxZoom: 19 }).addTo(map);
  } else {
    map.setView(center, map.getZoom());
  }

  renderMarkers();
};

onMounted(() => {
  nextTick(renderMap);
});

watch(
  () => [props.festival?.id, props.festival?.latitude, props.festival?.longitude, props.nearbyPlaces],
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
