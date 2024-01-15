import http from '@/plugins/http'
import type { Context } from '@/types/services'
import type { DAData } from '@/types/services/DA'

export function getRecommendation(context: any) {
  return http.post('/cab_recommendation/api/v1/recommendation', context)
}

export function getProcedure(event_type: string = 'ENG1: AUTO SHUTDOWN') {
  return http.post('/cab_recommendation/api/v1/procedure', {
    event: {
      event_type
    }
  })
}

export function getCorrelations(params: { size: number; app_id?: string; kpi_name?: string }) {
  return http.get('cab_correlation/api/v1/correlation', {
    params
  })
}

export function getContext() {
  return http.get<Context<DAData>>(`/cabcontext/api/v1/contexts?time=${Date.now()}`)
}
