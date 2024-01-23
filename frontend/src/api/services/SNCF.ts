import http from '@/plugins/http'
import type { RecommendationAction } from '@/types/services'

export function applyRecommendation(data: RecommendationAction) {
  return http.post(import.meta.env.VITE_SNCF_SIMU + '/transport_plan', data)
}
