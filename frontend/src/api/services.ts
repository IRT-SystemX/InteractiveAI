import http from '@/plugins/http'
import type { Context, Entity } from '@/types/entities'
import type { ContextResponse, Recommendation } from '@/types/services'
import type { Trace } from '@/types/trace'

// TODO: typing
export function getRecommendation<T extends Entity = Entity>(context: Context<T> | {}) {
  return http.post<Recommendation<T>[]>('/cab_recommendation/api/v1/recommendation', context)
}

export function getContext<E extends Entity = Entity>() {
  return http.get<ContextResponse<E>>(`/cabcontext/api/v1/contexts?time=${Date.now()}`)
}

export function sendTrace(payload: Trace) {
  return http.post<Required<Trace>>(import.meta.env.VITE_TRACE + '/api/v1/traces', {
    ...payload,
    date: new Date().toISOString()
  })
}
