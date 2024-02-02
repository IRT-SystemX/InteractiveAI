export type ORANGE = {
  Context: { [key: string]: any }
  Metadata: {
    bad_kpi: KPI
    event_type: 'APP_ANOMALY'
    id_app: `App_${number}`
  }
}

export type KPI = 'nb_err' | 'nb_pl' | 'nb_req' | 'delay_avg' | 'ratio_err' | 'ratio_pl'

export type CorrelationKey =
  | `App_${number}.KPI.${Exclude<KPI, 'ratio_err' | 'ratio_pl'>}`
  | `App_${number}.KPI_composite.${Extract<KPI, 'ratio_err' | 'ratio_pl'>}`

export type CorrelationData = { [key: CorrelationKey]: { [key: CorrelationKey]: number | null } }

export type CorrelationResponse = [
  {
    data: CorrelationData
    id_correlation: `${string}-${string}-${string}-${string}-${string}`
    timestamp_end: `${number}-${number}-${number}T${number}:${number}:${number}`
    timestamp_start: `${number}-${number}-${number}T${number}:${number}:${number}`
  }
]
