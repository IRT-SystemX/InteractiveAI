export type Railway = {
  AppData: {
    message: string
  }
  Context: {
    direction_agents: number[]
    list_of_target: {
      [key: `${number}`]: [number, number][]
    }
    position_agents: {
      [key: `${number}`]: [number, number]
    }
    trains: {
      failure: boolean
      id_train: string
      latitude: number
      longitude: number
      nb_passengers_connection: null
      nb_passengers_onboard: number
      speed: number
    }[]
  }
  Metadata: {
    event_type: 'PASSENGER' | 'INFRASTRUCTURE' | 'IMPACT' | 'HARDWARE'
    travel_plan?: { name: string; startDate: number; endDate?: number }[]
    id_train: string
    agent_id: string
    agent_position?: [number, number]
    latitude?: number
    longitude?: number
    delay: number
  }
  Action: {
    simulation_name: string
    targets_list: {
      agent_id: string
      targets: {
        passengers: number
        target_id: number
        target_type: 'STATION'
      }[]
    }[]
  }
}
