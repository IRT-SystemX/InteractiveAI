import http from '@/plugins/http'
import type { SNCF } from '@/types/entities/SNCF'

export function applyRecommendation(data: SNCF['Action']) {
  return http.post<{ message: string }>(import.meta.env.VITE_SNCF_SIMU + '/transport_plan', data)
}
