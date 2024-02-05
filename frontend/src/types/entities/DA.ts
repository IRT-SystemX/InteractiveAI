export type DA = {
  Context: {
    'Current airspeed': number
    Latitude: number
    Longitude: number
  }
  Metadata: { event_type: string; system: string }
}

export const Systems = ['STAT', 'ENG', 'ELEC', 'FUEL', 'HYD', 'ECS', 'BLD'] as const
export type System = (typeof Systems)[number]
