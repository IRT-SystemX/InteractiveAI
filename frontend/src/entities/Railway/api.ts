import http from '@/plugins/http'
import type { Action } from '@/types/entities'

export function applyRecommendation(data: Action<'Railway'>) {
  return http.post<{ message: string }>(import.meta.env.VITE_RAILWAY_SIMU + '/transport_plan', data)
}
