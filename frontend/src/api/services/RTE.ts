import http from '@/plugins/http'
import type { RecommendationAction } from '@/types/services'

// TODO: typing
export function applyRecommendation(data: RecommendationAction) {
  return http.post(import.meta.env.VITE_RTE_SIMU + '/api/v1/recommendations', data)
}
