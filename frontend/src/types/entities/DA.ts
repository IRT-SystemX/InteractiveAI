export type DA = {
  Context: {
    'Current airspeed': number
    Latitude: number
    Longitude: number
  }
  Metadata: { event_type: string; system: string }
  Action: null
}

export const Systems = ['STAT', 'ENG', 'ELEC', 'FUEL', 'HYD', 'ECS', 'BLD'] as const
export type System = (typeof Systems)[number]

export type Step = {
  taskIndex: number
  taskText: string
  taskType:
    | 'task'
    | 'monitor'
    | 'choice'
    | 'caution'
    | 'note'
    | 'flightpathAction'
    | 'operatingProcedure'
    | 'noActionRequired'
  state?: 'doing' | 'done'
}

export type Block = { blockIndex: 2; blockText: 'Monitor parameters'; tasks: Step[] }

export type Procedure = {
  max_speed: number
  min_speed: number
  procedure: Block[]
}
