import http from '@/plugins/http'
import type { RecommendationAction } from '@/types/services'

export function applyRecommendation(data: RecommendationAction) {
  return http.post(import.meta.env.VITE_RTE_SIMU + '/api/v1/recommendations', data)
}
