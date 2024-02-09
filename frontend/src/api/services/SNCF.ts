import http from '@/plugins/http'
import type { Action } from '@/types/entities'

export function applyRecommendation(data: Action<'SNCF'>) {
  return http.post<{ message: string }>(import.meta.env.VITE_SNCF_SIMU + '/transport_plan', data)
}
