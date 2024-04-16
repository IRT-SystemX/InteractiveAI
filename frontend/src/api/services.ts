import http from '@/plugins/http'
import type { Card } from '@/types/cards'
import type { Action, Context, Entity } from '@/types/entities'
import type { Procedure } from '@/types/procedure'
import type { ContextResponse, Recommendation, Trace } from '@/types/services'

export function getRecommendation<E extends Entity = Entity>(payload: {
  event: Card<E>['data']['metadata']
  context: Context<E>
}) {
  return http.post<Recommendation<E>[]>('/cab_recommendation/api/v1/recommendation', payload)
}

export function getContext<E extends Entity = Entity>() {
  return http.get<ContextResponse<E>>(`/cabcontext/api/v1/contexts?time=${Date.now()}`)
}

export function sendTrace(payload: Trace) {
  return http.post<Required<Trace>>('/cabhistoric/api/v1/traces', {
    ...payload,
    date: new Date().toISOString()
  })
}

export function applyRecommendation(data: Action) {
  return http.post<{ message: string }>('/api/v1/recommendations', data)
}

export function getProcedure(event_type: string) {
  return http.post<Procedure>('/cab_recommendation/api/v1/procedure', {
    event: {
      event_type
    }
  })
}
