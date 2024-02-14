import type { CorrelationResponse } from '@/entities/ORANGE/types'
import http from '@/plugins/http'
import type { Card } from '@/types/cards'

export function getCorrelations(params: { size: number; app_id?: string; kpi_name?: string }) {
  return http.get<CorrelationResponse>('cab_correlation/api/v1/correlation', {
    params
  })
}
export function correlation_feedback(card: Card, feedback: boolean) {
  const data = {
    card: card,
    feedback: feedback,
    feedback_date: Date.now()
  }
  console.log(data)
  return http.post('cab_correlation/api/v1/correlation/feedback', data)
}
