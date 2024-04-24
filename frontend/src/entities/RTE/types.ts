export type RTE = {
  Context: {
    observation: {
      _shunt_bus: number[]
      _shunt_p: number[]
      _shunt_q: number[]
      _shunt_v: number[]
      _thermal_limit: number[]
      a_ex: number[]
      a_or: number[]
      actual_dispatch: number[]
      attention_budget: [number]
      current_step: [number]
      curtailment: number[]
      curtailment_limit: number[]
      curtailment_limit_effective: number[]
      day: [number]
      day_of_week: [number]
      delta_time: [number]
      duration_next_maintenance: number[]
      gen_margin_down: number[]
      gen_margin_up: number[]
      gen_p: number[]
      gen_p_before_curtail: number[]
      gen_q: number[]
      gen_theta: number[]
      gen_v: number[]
      hour_of_day: [number]
      is_alarm_illegal: [boolean]
      last_alarm: number[]
      line_status: boolean[]
      load_p: number[]
      load_q: number[]
      load_theta: number[]
      load_v: number[]
      max_step: [number]
      minute_of_hour: [number]
      month: [number]
      p_ex: number[]
      p_or: number[]
      q_ex: number[]
      q_or: number[]
      rho: number[]
      storage_charge: []
      storage_power: []
      storage_power_target: []
      storage_theta: []
      support_theta: [boolean]
      target_dispatch: number[]
      theta_ex: number[]
      theta_or: number[]
      time_before_cooldown_line: number[]
      time_before_cooldown_sub: number[]
      time_next_maintenance: number[]
      time_since_last_alarm: [number]
      timestep_overflow: number[]
      topo_vect: number[]
      v_ex: number[]
      v_or: number[]
      was_alarm_used_after_game_over: [boolean]
      year: [number]
    }
    topology: string
  }
  Metadata: {
    event_type: 'KPI' | 'anticipation' | 'agent' | 'consignation'
    zone?: 'Est' | 'Ouest' | 'Centre'
    line: string
    flux: number | `${number}`
    kpis: {
      max_overload: string
      renewable_energy_share: number
      total_consumption: number
      distance_from_reference_topology: number
      redispatching_volume: number[]
    }
  }
  Action: {
    _change_bus_vect: boolean[]
    _curtail: number[]
    _raise_alarm: boolean[]
    _redispatch: number[]
    _set_line_status: number[]
    _set_topo_vect: number[]
    _storage_power: []
    _switch_line_status: boolean[]
  }
}
