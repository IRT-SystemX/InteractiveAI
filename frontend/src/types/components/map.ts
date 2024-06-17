import type { Severity } from '../cards'

export type Waypoint = {
  lat: number
  lng: number
  id: string
  category?: Uppercase<string>
  permanentTooltip?: boolean
  options?: Partial<{
    stroke: boolean
    radius: number
    color: string
    fillColor: string
    weight: number
    opacity: number
  }>
  severity?: Severity
}

export type Polyline = {
  id: string
  waypoints: Waypoint[]
  options?: {
    color?: string
  }
}
