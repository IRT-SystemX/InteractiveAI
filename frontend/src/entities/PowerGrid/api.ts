import http from '@/plugins/http'
import type { Action } from '@/types/entities'

export async function applyRecommendation(data: Action<'PowerGrid'>) {
  const base = import.meta.env.VITE_POWERGRID_SIMU
  const url = base + '/api/v1/recommendations'
  // Debug logging: confirm the apply action is actually sent to the simulator, and what is sent.
  // NB: the axios instance prepends baseURL (VITE_API), which is empty in standalone => same-origin.
  console.info(
    `[PowerGrid][apply] POST ${url}  (axios baseURL="${import.meta.env.VITE_API ?? ''}", VITE_POWERGRID_SIMU="${base ?? ''}")`
  )
  console.info('[PowerGrid][apply] payload sent to simulator:', data)
  try {
    const res = await http.post<{ message: string }>(url, data)
    const raw: unknown = res.data
    const looksLikeHtml = typeof raw === 'string' && /<!doctype html|<html/i.test(raw)
    const body =
      typeof raw === 'string' && raw.length > 300 ? raw.slice(0, 300) + '… (truncated)' : res.data
    console.info(`[PowerGrid][apply] simulator responded HTTP ${res.status}:`, body)
    if (looksLikeHtml)
      console.warn(
        '[PowerGrid][apply] ⚠ Response is the SPA index.html, NOT a simulator reply. The request ' +
          'fell through to the nginx SPA fallback — there is no /powergrid-simu/ proxy in the running ' +
          'nginx config, so the action never reached the simulator.'
      )
    return res
  } catch (err) {
    const e = err as { response?: { status?: number; data?: unknown }; message?: string }
    console.error(
      '[PowerGrid][apply] request FAILED — HTTP',
      e.response?.status ?? '(no response / network error)',
      e.response?.data ?? e.message ?? err
    )
    throw err
  }
}
