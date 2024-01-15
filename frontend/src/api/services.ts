import http from '@/plugins/http'
import type { Entity } from '@/types/entities'
import type { Context } from '@/types/services'
import type { DAData } from '@/types/services/DA'
import type { TraceType } from '@/types/trace'

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

export function sendTrace(payload: { data: object; date?: Date; step: TraceType; use_case: Entity }) {
  return http.post(import.meta.env.VITE_TRACE + '/api/v1/traces', { ...payload, date: new Date().toISOString() })
}

export function applyRecommendationRTE(data: any) {
  return http.post(import.meta.env.VITE_RTE_SIMU + '/api/v1/recommendations', data)
}

export function applyRecommendationSNCF(data: any) {
  return http.post(import.meta.env.VITE_SNCF_SIMU + '/transport_plan', data)
}
