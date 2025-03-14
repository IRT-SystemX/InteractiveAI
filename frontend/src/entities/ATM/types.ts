export type ATM = {
  Context: {
    'Current airspeed': number
    Latitude: number
    Longitude: number
    ApDest?: {
      apcity: string
      apid: Uppercase<string>
      aplat: number
      aplon: number
      apname: string
    }
    wpList?: {
      wpid: Uppercase<string>
      wpidx: number
      wplat: number
      wplon: number
    }[]
  }
  Metadata: { event_type: string; system: string }
  Action: {
    airport_destination: {
      apcity: string
      apid: Uppercase<string>
      apname: Uppercase<string>
      latitude: number
      longitude: number
    }
    waypoints: {
      wplat: number
      wplon: number
      wpidx: number
      wpid: Uppercase<string>
    }[]
  }
}

export const SYSTEMS = [
  'ENGINE',
  'ELECTRIC',
] as const
Object.freeze(SYSTEMS)
export type System = (typeof SYSTEMS)[number]
