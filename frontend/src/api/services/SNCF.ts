import type { Action } from '@/entities/entities'
import http from '@/plugins/http'

export function applyRecommendation(data: Action<'SNCF'>) {
  return http.post<{ message: string }>(import.meta.env.VITE_SNCF_SIMU + '/transport_plan', data)
}
