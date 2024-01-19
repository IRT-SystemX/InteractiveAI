export type Context = { [key: string]: any }

type KPI = 'nb_err' | 'nb_pl' | 'nb_req' | 'delay_avg' | 'ratio_err' | 'ratio_pl'

export type Metadata = {
  bad_kpi: KPI
  event_type: 'APP_ANOMALY'
  id_app: `App_${number}`
}
