<template>
  <div id="map"></div>
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

import L, { type CircleMarkerOptions, type PolylineOptions } from 'leaflet'
import { LocateFixed, LocateOff } from 'lucide-vue-next'
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import { useMapStore } from '@/stores/components/map'

const props = withDefaults(
  defineProps<{
    tileLayers?: string[]
    smoothMovements?: boolean
  }>(),
  { tileLayers: () => ['http://{s}.tile.osm.org/{z}/{x}/{y}.png'], smoothMovements: true }
)
const mapStore = useMapStore()
const route = useRoute()

let map: L.Map | undefined = undefined

const lockView = ref(true)
const waypointsL = ref<{ id: string; L: L.CircleMarker }[]>([])
const contextWaypointsL = ref<{ id: string; L: L.Marker }[]>([])
const polylinesL = ref<{ id: string; L: L.Polyline }[]>([])

watch(lockView, (value) => {
  if (value) {
    if (mapStore.contextWaypoints.length === 1)
      map!.setView(mapStore.contextWaypoints[0], map?.getZoom())
    if (mapStore.contextWaypoints.length > 1)
      map!.fitBounds(L.latLngBounds(mapStore.contextWaypoints), { maxZoom: map?.getZoom() })
  }
})

onMounted(() => {
  map = L.map('map', {
    center: L.latLng(47, 2),
    zoom: 6
  })

  L.control.scale().addTo(map)

  map.createPane('polylines')
  map.createPane('waypoints')

  for (const tileLayer of props.tileLayers) L.tileLayer(tileLayer).addTo(map)

  watch(
    mapStore.waypoints,
    (waypoints) => {
      for (const deleted of waypointsL.value) deleted.L.remove()

      for (const waypoint of waypoints) {
        const marker = L.circleMarker(waypoint, {
          pane: 'waypoints',
          color: '#fff',
          stroke: false,
          fillOpacity: 1,
          ...(waypoint.options as CircleMarkerOptions)
        })
          .bindTooltip(waypoint.id, { direction: 'top' })
          .addTo(map!)
        waypointsL.value.push({ id: waypoint.id, L: marker })
      }
    },
    { immediate: true }
  )
  watch(
    mapStore.contextWaypoints,
    (value, old) => {
      if (!old) return

      if (lockView.value) {
        if (value.length === 1) map!.setView(value[0], map?.getZoom())
        if (value.length > 1) map!.fitBounds(L.latLngBounds(value), { maxZoom: map?.getZoom() })
      }

      for (const waypoint of value) {
        const existing = contextWaypointsL.value.find((el) => el.id === waypoint.id)
        if (existing) {
          existing.L.setLatLng(waypoint)
          existing.L.setIcon(
            L.icon({
              iconUrl: `/img/icons/map_markers/${route.params.entity}.svg`,
              iconSize: [32, 32],
              className: 'context-marker ' + waypoint.options?.severity
            })
          )
          continue
        }

        const marker = L.marker(waypoint, {
          pane: 'waypoints',
          icon: L.icon({
            iconUrl: `/img/icons/map_markers/${route.params.entity}.svg`,
            iconSize: [32, 32],
            className: 'context-marker ' + waypoint.options?.severity
          })
        })
          .bindTooltip(waypoint.id, { direction: 'top', offset: [0, -16] })
          .addTo(map!)
        contextWaypointsL.value.push({ id: waypoint.id, L: marker })
      }
      for (const deleted of old.filter(
        (oldElement) => !value.some((newElement) => newElement.id === oldElement!.id)
      ))
        contextWaypointsL.value.find((el) => el.id === deleted!.id)?.L.remove()
    },
    { immediate: true }
  )
  watch(
    mapStore.polylines,
    (polylines) => {
      for (const deleted of polylinesL.value) deleted.L.remove()

      for (const polyline of polylines) {
        const marker = L.polyline(polyline.waypoints, {
          pane: 'polylines',
          weight: 10,
          color: 'var(--color-primary)',
          ...(polyline.options as PolylineOptions)
        }).addTo(map!)
        polylinesL.value.push({ id: polyline.id, L: marker })
      }
    },
    { immediate: true }
  )
})

onBeforeUnmount(() => {
  map?.remove()
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
  padding: calc(var(--unit) / 2);
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
