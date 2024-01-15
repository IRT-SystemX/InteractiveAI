import type { CircleMarkerOptions } from 'leaflet'
import { defineStore } from 'pinia'
import { ref } from 'vue'

import type { Severity } from '@/types/cards'
import type { Polyline, Waypoint } from '@/types/map'
import { addOrUpdate, remove } from '@/utils/utils'

export const useMapStore = defineStore('map', () => {
  const waypoints = ref<Waypoint<CircleMarkerOptions>[]>([])
  const polylines = ref<Polyline[]>([])
  const contextWaypoints = ref<Waypoint<{ severity?: Severity }>[]>([])

  function reset() {
    resetWaypoints()
    resetPolylines()
    resetContextWaypoints()
  }

  function addWaypoint(waypoint: Waypoint<CircleMarkerOptions>) {
    addOrUpdate(waypoints.value, waypoint, (el) => el.id === waypoint.id)
  }

  function removeWaypoint(waypoint: Waypoint<CircleMarkerOptions>) {
    remove(waypoints.value, (el) => el.id === waypoint.id)
  }

  function resetWaypoints() {
    waypoints.value.splice(0, waypoints.value.length)
  }
  function addPolyline(polyline: Polyline) {
    addOrUpdate(polylines.value, polyline, (el) => el.id === polyline.id)
  }

  function removePolyline(polyline: Polyline) {
    remove(polylines.value, (el) => el.id === polyline.id)
  }

  function resetPolylines() {
    polylines.value.splice(0, polylines.value.length)
  }
  function addContextWaypoint(waypoint: Waypoint<{ severity?: Severity }>) {
    addOrUpdate(contextWaypoints.value, waypoint, (el) => el.id === waypoint.id)
  }

  function removeContextWaypoint(waypoint: Waypoint<{ severity?: Severity }>) {
    remove(contextWaypoints.value, (el) => el.id === waypoint.id)
  }

  function resetContextWaypoints() {
    contextWaypoints.value.splice(0, contextWaypoints.value.length)
  }

  return {
    waypoints,
    polylines,
    contextWaypoints,
    reset,
    addWaypoint,
    removeWaypoint,
    resetWaypoints,
    addPolyline,
    removePolyline,
    resetPolylines,
    addContextWaypoint,
    removeContextWaypoint,
    resetContextWaypoints
  }
})
