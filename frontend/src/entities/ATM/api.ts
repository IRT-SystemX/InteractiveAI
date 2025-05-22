import http from '@/plugins/http'
import type { Action } from '@/types/entities'

export function applyRecommendation(data: Action<'ATM'>) {
  return http.post<{ message: string }>(import.meta.env.VITE_ATM_SIMU + '/update-flight-plan', data)
}
