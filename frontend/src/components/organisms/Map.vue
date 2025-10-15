<template>
  <LMap ref="map" v-model:zoom="zoom" :center="[47, 2]" :max-bounds-viscosity="0.5">
    <LTileLayer
      v-for="tileLayer of tileLayers"
      :key="tileLayer"
      :url="tileLayer"
      layer-type="base"
      name="OpenStreetMap" />
    <LPolyline
      v-for="polyline of mapStore.polylines"
      :key="polyline.id"
      :color="
        polyline.options?.color || `var(--color-${criticalityToColor(maxCriticality('ROUTINE'))})`
      "
      :weight="8"
      :lat-lngs="polyline.waypoints" />
    <LCircleMarker
      v-for="waypoint of mapStore.waypoints"
      :key="waypoint.id"
      :lat-lng="[waypoint.lat, waypoint.lng]"
      :color="`var(--color-${criticalityToColor(maxCriticality('ROUTINE'))})`"
      fill-color="#fff"
      :weight="2"
      :fill-opacity="1"
      :radius="8"
      v-bind="waypoint.options"
      @click="waypointClick">
      <LTooltip
        :options="{
          permanent: waypoint.permanentTooltip,
          direction: 'top',
          offset: [0, waypoint.options?.radius ? -waypoint.options?.radius : -8]
        }">
        {{ waypoint.id }}
      </LTooltip>
    </LCircleMarker>
    <LMarker
      v-for="waypoint of mapStore.contextWaypoints"
      :key="waypoint.id"
      :lat-lng="[waypoint.lat, waypoint.lng]"
      :z-index-offset="10000"
      @click="contextClick">
      <LTooltip
        :options="{ permanent: waypoint.permanentTooltip, direction: 'top', offset: [0, -12] }">
        {{ waypoint.id }}
      </LTooltip>
      <LIcon
        :icon-url="`/img/icons/map_markers/${$route.params.entity}.svg`"
        :icon-size="[32, 32]"
        class="context-marker"
        :class-name="'context-marker ' + waypoint.severity" />
    </LMarker>
    <LControlScale />
  </LMap>
  <label class="cab-map-lockview p-1 flex flex-wrap">
    <input v-model="lockView" type="checkbox" style="display: none" @change="toggleLockView" />
    <div class="ml-1">
      <LocateFixed v-if="lockView" />
      <LocateOff v-else />
    </div>
    {{ lockView ? $t('map.lockview') : $t('map.no_lockview') }}
  </label>
</template>
<script setup lang="ts">
import 'leaflet/dist/leaflet.css'

import {
  LCircleMarker,
  LControlScale,
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

import { useAppStore } from '@/stores/app'
import { useMapStore } from '@/stores/components/map'
import type { Waypoint } from '@/types/components/map'
import { criticalityToColor, maxCriticality } from '@/utils/utils'

const props = withDefaults(
  defineProps<{
    tileLayers?: string[]
    contextClick?: (waypoint: Waypoint) => void
    waypointClick?: (waypoint: Waypoint) => void
    autoFit?: boolean
  }>(),
  {
    tileLayers: () => ['http://{s}.tile.osm.org/{z}/{x}/{y}.png'],
    contextClick: undefined,
    waypointClick: undefined
  }
)

const mapStore = useMapStore()
const appStore = useAppStore()

const lockView = ref(true)
const zoom = ref(6)
const map = ref()

watch(
  () => mapStore.contextWaypoints, 
  () => {
    if (props.autoFit) {
      toggleLockView()
    }
  
}
)


watch(appStore.panels, () => {
  map.value.leafletObject.invalidateSize()
})

function toggleLockView() {
  if (!lockView.value) {
    map.value.leafletObject.setMaxBounds()
  } else {
    map.value.leafletObject.setMaxBounds(latLngBounds(mapStore.contextWaypoints), {
      maxZoom: zoom.value
    })
  }
}

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
