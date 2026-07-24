import type { CognitiveSnapshot } from '@/api/cognitive'
import http from '@/plugins/http'
import { useAppStore } from '@/stores/app'
import { useCardsStore } from '@/stores/cards'
import { useServicesStore } from '@/stores/services'
import type { Card } from '@/types/cards'
import type { Action, Context, Entity } from '@/types/entities'
import type { Procedure } from '@/types/procedure'
import type { FullContext, Recommendation, Trace } from '@/types/services'
import { recordTraceForSession } from '@/utils/traceSessionExport'

export function getRecommendation<E extends Entity = Entity>(payload: {
  event: Card<E>['data']['metadata']
  context: Context<E>
  cognitive_snapshot?: CognitiveSnapshot
}) {
  return http.post<Recommendation<E>[]>('/cab_recommendation/api/v1/recommendation', payload)
}

export function getContext<E extends Entity = Entity>() {
  return http.get<FullContext<E>[]>(`/cabcontext/api/v1/contexts?time=${Date.now()}`)
}

export function sendTrace(payload: Trace) {
  if (payload.step === 'ASKFORHELP' && typeof payload.data === 'object' && payload.data !== null) {
    const cardId = (payload.data as { id?: unknown }).id
    if (typeof cardId === 'string') {
      const cardsStore = useCardsStore()
      const card = cardsStore._cards.find((item) => item.id === cardId)
      recordTraceForSession({
        use_case: payload.use_case,
        step: 'EVENT',
        data: {
          card_id: cardId,
          process_instance_id: card?.processInstanceId,
          start_date: card?.startDate ? new Date(card.startDate).toISOString() : undefined,
          title: card?.titleTranslated || card?.title?.parameters?.title || '',
          summary: card?.summaryTranslated || card?.summary?.parameters?.summary || '',
          metadata: card?.data.metadata
        },
        date: new Date().toISOString()
      })
    }
  }

  const tracePayload = {
    ...payload,
    date: new Date().toISOString()
  }
  recordTraceForSession(tracePayload)
  return http.post<Required<Trace>>('/cabhistoric/api/v1/traces', tracePayload)
}

// TODO: TEMP HACK (eval-demo) — MUST BE REMOVED before next release
// The real API call is disabled and replaced with a fake success response for demo purposes.
export function applyRecommendation<E extends Entity = Entity>(data: Action<E>) {
  // [DISABLED] Simulator API is inactive — returning fake success for demo
  // To restore: uncomment the http.post and remove the Promise.resolve
  // return http.post<{ message: string }>('/api/v1/recommendations', data)
  return Promise.resolve({ data: { message: 'ok (simulated)' } }) // TEMP HACK: remove this line
}

export function getProcedure(event_type: string) {
  return http.post<Procedure>('/cab_recommendation/api/v1/procedure', {
    event: {
      event_type
    }
  })
}
export function sendFeedback<E extends Entity = Entity>(
  recommendation: Recommendation<E>,
  feedback = false
) {
  const card = useAppStore()._card!
  return http.post('/cab_capitalization/api/v1/feedbacks', {
    event_id: card.processInstanceId,
    context_id: useServicesStore().context(card.entityRecipients[0])?.id_context,
    recommandation: recommendation,
    feedback: feedback,
    feedback_date: new Date().toISOString(),
    use_case: card.entityRecipients[0]
  })
}
