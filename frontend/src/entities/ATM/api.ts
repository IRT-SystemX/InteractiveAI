import http from '@/plugins/http'
import type { Action } from '@/types/entities'

// TODO: TEMP HACK (eval-demo) — MUST BE REMOVED before next release
// The real ATM simulator API call is disabled and replaced with a fake success response for demo purposes.
export function applyRecommendation(data: Action<'ATM'>) {
  // [DISABLED] Simulator API is inactive — returning fake success for demo
  // To restore: uncomment the http.post and remove the Promise.resolve
  // return http.post<{ message: string }>(import.meta.env.VITE_ATM_SIMU + '/update-flight-plan', data)
  return Promise.resolve({ data: { message: 'ok (simulated)' } }) // TEMP HACK: remove this line
}
