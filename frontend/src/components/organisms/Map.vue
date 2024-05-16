<template>
  <l-map ref="map" v-model:zoom="zoom" :center="[47, 2]">
    <l-tile-layer
      v-for="tileLayer of tileLayers"
      :key="tileLayer"
      :url="tileLayer"
      layer-type="base"
      name="OpenStreetMap"></l-tile-layer>
    <l-polyline
      v-for="polyline of mapStore.polylines"
      :key="polyline.id"
      :color="polyline.options?.color || 'var(--color-primary)'"
      :weight="8"
      :lat-lngs="polyline.waypoints"></l-polyline>
    <l-circle-marker
      v-for="waypoint of mapStore.waypoints"
      :key="waypoint.id"
      :lat-lng="[waypoint.lat, waypoint.lng]"
      color="var(--color-primary)"
      fill-color="#fff"
      :weight="2"
      :fill-opacity="1"
      :radius="8"
      v-bind="waypoint.options">
      <l-tooltip :options="{ permanent: waypoint.permanentTooltip, direction: 'top' }">
        {{ waypoint.id }}
      </l-tooltip>
    </l-circle-marker>
    <l-marker
      v-for="waypoint of mapStore.contextWaypoints"
      :key="waypoint.id"
      :lat-lng="[waypoint.lat, waypoint.lng]"
      :z-index-offset="10000">
      <l-tooltip :options="{ permanent: waypoint.permanentTooltip, direction: 'top' }">
        {{ waypoint.id }}
      </l-tooltip>
      <l-icon
        :icon-url="`/img/icons/map_markers/${$route.params.entity}.svg`"
        :icon-size="[32, 32]"
        class="context-marker"
        :class-name="'context-marker ' + waypoint.severity"></l-icon>
    </l-marker>
  </l-map>
  <label class="cab-map-lockview p-1 flex flex-wrap">
    <input v-model="lockView" type="checkbox" style="display: none" />
    <div class="ml-1">
      <LocateFixed v-if="lockView" />
      <LocateOff v-else />
    </div>
    {{ lockView ? $t('map.lockview') : $t('map.no-lockview') }}
  </label>
</template>
<script setup lang="ts">
import 'leaflet/dist/leaflet.css'

import {
  LCircleMarker,
  LIcon,
  LMap,
  LMarker,
  LPolyline,
  LTileLayer,
  LTooltip
} from '@vue-leaflet/vue-leaflet'
import { latLngBounds } from 'leaflet'
import { LocateFixed, LocateOff } from 'lucide-vue-next'
import { onUnmounted, ref, watch } from 'vue'

import { useMapStore } from '@/stores/components/map'

const mapStore = useMapStore()

const lockView = ref(true)
const zoom = ref(6)

const map = ref()

withDefaults(
  defineProps<{
    tileLayers?: string[]
  }>(),
  { tileLayers: () => ['http://{s}.tile.osm.org/{z}/{x}/{y}.png'] }
)

watch(mapStore.contextWaypoints, (value) => {
  if (lockView.value)
    map.value.leafletObject.fitBounds(latLngBounds(value), {
      maxZoom: zoom.value
    })
})

onUnmounted(() => {
  mapStore.reset()
})
</script>
<style lang="scss">
#map {
  height: 100%;
  width: 100%;
}

.context-marker {
  transition: var(--duration);
  background: var(--color-success);
  border-radius: var(--radius-circular);
  padding: calc(var(--unit) / 2) !important;
  &.ACTION {
    background: var(--color-warning);
  }
  &.ALARM {
    background: var(--color-error);
  }
}
.cab-map-lockview {
  width: calc(var(--unit) * 5);
  display: flex;
  flex-direction: row-reverse;
  align-items: flex-start;
  max-width: fit-content;
  height: calc(var(--unit) * 5);
  overflow: hidden;
  text-overflow: clip;
  position: absolute;
  z-index: 1000;
  background: var(--color-background);
  border-radius: var(--radius-small);
  top: var(--spacing-1);
  right: var(--spacing-1);
  transition: var(--duration);

  &:hover {
    width: 100%;
  }
}
</style>
