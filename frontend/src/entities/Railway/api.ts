import http from '@/plugins/http'
import type { Action } from '@/types/entities'

// TODO: TEMP HACK (eval-demo) — MUST BE REMOVED before next release
// The real Railway simulator API call is disabled and replaced with a fake success response for demo purposes.
// To restore: uncomment the http.post line and delete the Promise.resolve line.
export function applyRecommendation(data: Action<'Railway'>) {
  // [DISABLED] Simulator API is inactive — returning fake success for demo
  // To restore: uncomment the http.post and remove the Promise.resolve
  // return http.post<{ message: string }>(import.meta.env.VITE_RAILWAY_SIMU + '/transport_plan', data)
  return Promise.resolve({ data: { message: 'ok (simulated)' } }) // TEMP HACK: remove this line
}
