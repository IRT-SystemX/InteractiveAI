import http from '@/plugins/http'
import type { RTE } from '@/types/entities/RTE'

// TODO: typing
export function applyRecommendation(data: RTE['Action']) {
  return http.post(import.meta.env.VITE_RTE_SIMU + '/api/v1/recommendations', data)
}
