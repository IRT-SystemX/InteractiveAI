import http from '@/plugins/http'
import type { Action } from '@/types/entities'

export function applyRecommendation(data: Action<'RTE'>) {
  return http.post<{ message: string }>(
    import.meta.env.VITE_RTE_SIMU + '/api/v1/recommendations',
    data
  )
}
