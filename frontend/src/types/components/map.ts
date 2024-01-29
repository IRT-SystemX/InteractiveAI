import type { CircleMarkerOptions, PolylineOptions } from 'leaflet'

export type Waypoint<T> = {
  lat: number
  lng: number
  id: string
  options?: T
}

export type Polyline = {
  id: string
  waypoints: Waypoint<CircleMarkerOptions>[]
  options?: PolylineOptions
}
