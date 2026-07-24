import { fetchCognitiveSnapshot } from '@/api/cognitive'
import type { CognitiveSnapshot } from '@/api/cognitive'
import type { Trace } from '@/types/services'
import { hasCognitiveConsent } from '@/utils/consent'

type ExportFormat = 'json' | 'csv'
type SessionStep = Trace['step'] | 'FEEDBACK'

type StoredTrace = {
  date: string
  use_case: Trace['use_case']
  step: SessionStep
  data: unknown
}

type TraceSession = {
  sessionId: string
  startedAt: string
  userLogin?: string
  traces: StoredTrace[]
}

type ExportOptions = {
  force?: boolean
  userLogin?: string
}

const STORAGE_KEY = 'interactiveai.trace-session.v1'

function generateSessionId() {
  if (window.isSecureContext && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID()
  }
  return '10000000-1000-4000-8000-100000000000'.replace(/[018]/g, (char) =>
    (+char ^ (crypto.getRandomValues(new Uint8Array(1))[0] & (15 >> (+char / 4)))).toString(16)
  )
}

function createSession(userLogin?: string): TraceSession {
  return {
    sessionId: generateSessionId(),
    startedAt: new Date().toISOString(),
    userLogin,
    traces: []
  }
}

function loadSession(): TraceSession | undefined {
  const raw = localStorage.getItem(STORAGE_KEY)
  if (!raw) return undefined
  try {
    return JSON.parse(raw) as TraceSession
  } catch {
    localStorage.removeItem(STORAGE_KEY)
    return undefined
  }
}

function saveSession(session: TraceSession) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(session))
}

function eventKey(data: unknown): string | undefined {
  if (!data || typeof data !== 'object') return undefined
  const candidate = data as { card_id?: unknown; process_instance_id?: unknown }
  if (typeof candidate.card_id === 'string') return `card:${candidate.card_id}`
  if (typeof candidate.process_instance_id === 'string') return `process:${candidate.process_instance_id}`
  return undefined
}

/**
 * Build a structured view: nest ASKFORHELP/FEEDBACK/AWARD under the EVENT they belong to.
 *
 * Algorithm:
 *  1. Walk traces in chronological order.
 *  2. Every EVENT becomes a top-level structured entry (with an `interactions` array).
 *  3. An ASKFORHELP opens a "current interaction group" linked to an EVENT via card_id.
 *  4. Subsequent FEEDBACK / AWARD traces are appended to that group until a new ASKFORHELP or EVENT appears.
 *  5. Traces that cannot be linked to any EVENT remain at the top level as-is.
 */
type StructuredEvent = StoredTrace & {
  interactions: StoredTrace[]
  /** Time in ms between ASKFORHELP and AWARD. null when the user didn't choose a solution. */
  decision_time_ms: number | null
}

type StructuredTrace = StoredTrace | StructuredEvent

type SessionKpis = {
  /** Total session duration in ms (endedAt − startedAt) */
  total_session_time_ms: number
  /** Average decision time across ALL events (sum of decision times / total events). null if no events. */
  avg_decision_time_ms: number | null
}

function isStructuredEvent(t: StructuredTrace): t is StructuredEvent {
  return 'interactions' in t
}

function computeDecisionTime(interactions: StoredTrace[]): number | null {
  let askDate: string | undefined
  let awardDate: string | undefined
  for (let i = 0; i < interactions.length; i++) {
    if (interactions[i].step === 'ASKFORHELP' && !askDate) askDate = interactions[i].date
    if (interactions[i].step === 'AWARD' && !awardDate) awardDate = interactions[i].date
  }
  if (!askDate || !awardDate) return null
  return new Date(awardDate).getTime() - new Date(askDate).getTime()
}

/** Map legacy event_type values to human-readable labels for export. */
function normalizeEventType(eventType: string): string {
  if (eventType === 'KPI') return 'Overload'
  return eventType
}

function buildStructuredTraces(flat: StoredTrace[]): StructuredTrace[] {
  // Index: card_id → structured event entry
  const eventByCardId: Record<string, StructuredEvent> = {}
  const result: StructuredTrace[] = []

  // Pointer to the currently "active" interaction group
  let currentEvent: StructuredEvent | undefined

  for (const trace of flat) {
    if (trace.step === 'EVENT') {
      const structured: StructuredEvent = { ...trace, interactions: [], decision_time_ms: null }
      const data = trace.data as Record<string, unknown> | undefined
      const cardId = data?.card_id as string | undefined
      if (cardId) eventByCardId[cardId] = structured
      result.push(structured)
      // Don't change currentEvent here – EVENTs are async / independent
      continue
    }

    if (trace.step === 'ASKFORHELP') {
      // Resolve the parent EVENT via the card id stored in data.id
      const data = trace.data as Record<string, unknown> | undefined
      const cardId = data?.id as string | undefined
      const parent = cardId ? eventByCardId[cardId] : undefined
      if (parent) {
        currentEvent = parent
        currentEvent.interactions.push(trace)
      } else {
        // Orphan ASKFORHELP – keep at top level
        currentEvent = undefined
        result.push(trace)
      }
      continue
    }

    // FEEDBACK / AWARD / anything else → attach to current group if open
    if (currentEvent) {
      currentEvent.interactions.push(trace)
    } else {
      result.push(trace)
    }
  }

  // Compute per-event decision time KPIs
  for (const entry of result) {
    if (isStructuredEvent(entry)) {
      entry.decision_time_ms = computeDecisionTime(entry.interactions)
    }
  }

  return result
}

function escapeCsv(value: unknown): string {
  const normalized = typeof value === 'string' ? value : JSON.stringify(value)
  return `"${(normalized ?? '').replace(/"/g, '""')}"`
}

function buildCsv(session: TraceSession, endedAt: string) {
  const header = [
    'session_id',
    'user_login',
    'session_started_at',
    'session_ended_at',
    'trace_date',
    'use_case',
    'step',
    'data'
  ]

  const rows = session.traces.map((trace) =>
    [
      session.sessionId,
      session.userLogin ?? '',
      session.startedAt,
      endedAt,
      trace.date,
      trace.use_case,
      trace.step,
      trace.data
    ]
      .map((item) => escapeCsv(item))
      .join(',')
  )

  return [header.join(','), ...rows].join('\n')
}

function formatMs(ms: number | null): string {
  if (ms === null) return '—'
  if (ms < 1000) return ms + ' ms'
  const totalSec = Math.round(ms / 1000)
  const min = Math.floor(totalSec / 60)
  const sec = totalSec % 60
  return min > 0 ? min + 'm ' + sec + 's' : sec + 's'
}

function escapeHtml(str: string): string {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

function formatTime(iso: string): string {
  try {
    return new Date(iso).toLocaleString()
  } catch {
    return iso
  }
}

function stepBadge(step: string): string {
  const colors: Record<string, string> = {
    EVENT: '#2563eb',
    ASKFORHELP: '#d97706',
    FEEDBACK: '#7c3aed',
    AWARD: '#059669',
    SOLUTION: '#0891b2'
  }
  const bg = colors[step] || '#6b7280'
  return '<span style="display:inline-block;padding:2px 8px;border-radius:4px;color:#fff;font-size:12px;font-weight:600;background:' + bg + '">' + escapeHtml(step) + '</span>'
}

function feedbackLabel(data: unknown): string {
  if (!data || typeof data !== 'object') return ''
  const d = data as Record<string, unknown>
  const action = typeof d.action === 'string' ? d.action : ''
  const rec = typeof d.recommendation === 'string' ? d.recommendation : ''
  if (action === 'confirm_recommendation') return '<span style="color:#059669">&#10003; Confirmed</span> — ' + escapeHtml(rec)
  if (action === 'downvote_recommendation') return '<span style="color:#dc2626">&#10007; Downvoted</span> — ' + escapeHtml(rec)
  if (action === 'dismiss_kpi') return '<span style="color:#6b7280">Dismissed KPI</span>'
  return escapeHtml(action) + (rec ? ' — ' + escapeHtml(rec) : '')
}

/** Max character length for a single value rendered in the HTML summary. */
const MAX_VALUE_LENGTH = 200

/** Return a safe, human-readable representation of a value, truncating if too large. */
function safeValue(val: unknown): string {
  if (val === null || val === undefined) return ''
  const str = typeof val === 'string' ? val : JSON.stringify(val)
  if (str.length <= MAX_VALUE_LENGTH) return str
  return str.slice(0, MAX_VALUE_LENGTH) + '\u2026 [truncated]'
}

/** Returns true when a value looks like encrypted / binary blob data. */
function isLargeBlob(val: unknown): boolean {
  if (val === null || val === undefined) return false
  const str = typeof val === 'string' ? val : JSON.stringify(val)
  return str.length > MAX_VALUE_LENGTH
}

function eventMetadataHtml(data: unknown): string {
  if (!data || typeof data !== 'object') return ''
  const d = data as Record<string, unknown>
  const meta = d.metadata as Record<string, unknown> | undefined
  if (!meta) return ''
  const rows: string[] = []
  const keys = Object.keys(meta)
  for (let i = 0; i < keys.length; i++) {
    const key = keys[i]
    const val = meta[key]
    if (key === 'event_context' && isLargeBlob(val) && typeof val === 'string') {
      const src = val.startsWith('data:') ? val : 'data:image/png;base64,' + val
      rows.push('<tr><td style="padding:2px 10px 2px 0;color:#6b7280;font-size:13px;vertical-align:top">' + escapeHtml(key) + '</td><td><img src="' + src + '" style="width:600px;max-width:100%;border-radius:4px;margin-top:4px;cursor:zoom-in" alt="event context image" onclick="this.style.width=this.style.width===\'100%\'?\'600px\':\'100%\'"></td></tr>')
    } else if (isLargeBlob(val)) {
      rows.push('<tr><td style="padding:2px 10px 2px 0;color:#6b7280;font-size:13px">' + escapeHtml(key) + '</td><td style="font-size:13px;color:#9ca3af;font-style:italic">[large data omitted]</td></tr>')
    } else {
      rows.push('<tr><td style="padding:2px 10px 2px 0;color:#6b7280;font-size:13px">' + escapeHtml(key) + '</td><td style="font-size:13px">' + escapeHtml(safeValue(val)) + '</td></tr>')
    }
  }
  return '<table style="margin:4px 0 0 16px">' + rows.join('') + '</table>'
}

function cognitiveSnapshotHtml(data: unknown): string {
  if (!data || typeof data !== 'object') return ''
  const d = data as Record<string, unknown>
  const snapshot = d.cognitive_snapshot as CognitiveSnapshot | null | undefined
  if (!snapshot) return ''

  const { cognitive_performance: cp, stress_state: ss, cognitive_performance_explainability: cpExp, stress_explainability: ssExp, error } = snapshot

  let html = '<div style="margin:8px 0;padding:8px 12px;background:#f0f4ff;border-left:3px solid #6366f1;border-radius:4px;font-size:13px">'
  html += '<div style="font-weight:600;color:#4338ca;margin-bottom:6px">&#129504; User\'s cognitive informations </div>'

  if (error) {
    html += '<div style="color:#dc2626;font-size:12px">&#9888; ' + escapeHtml(error) + '</div>'
    html += '</div>'
    return html
  }

  if (cp) {
    html += '<div style="margin-bottom:3px"><span style="color:#6b7280">Cognitive Performance:</span> <b>' + escapeHtml(cp.value) + '</b> <span style="color:#9ca3af;font-size:11px">' + escapeHtml(cp.timestamp) + '</span></div>'
  } else {
    html += '<div style="margin-bottom:3px;color:#9ca3af">Cognitive Performance: —</div>'
  }
  if (ss) {
    const stressed = ss.value === '1'
    const stressLabel = stressed
      ? '<span style="color:#dc2626;font-weight:600">&#9888; Stressed</span>'
      : '<span style="color:#059669;font-weight:600">&#10003; Not stressed</span>'
    html += '<div style="margin-bottom:3px"><span style="color:#6b7280">Stress State:</span> ' + stressLabel + ' <span style="color:#9ca3af;font-size:11px">' + escapeHtml(ss.timestamp) + '</span></div>'
  } else {
    html += '<div style="margin-bottom:3px;color:#9ca3af">Stress State: —</div>'
  }
  if (cpExp) {
    html += '<div style="margin-bottom:3px"><span style="color:#6b7280">Cognitive Performance Explainability:</span> ' + escapeHtml(cpExp.value) + '</div>'
  } else {
    html += '<div style="margin-bottom:3px;color:#9ca3af">Cognitive Performance Explainability: —</div>'
  }
  if (ssExp) {
    html += '<div><span style="color:#6b7280">Stress Explainability:</span> ' + escapeHtml(ssExp.value) + '</div>'
  } else {
    html += '<div style="color:#9ca3af">Stress Explainability: —</div>'
  }
  html += '</div>'
  return html
}

function awardHtml(trace: StoredTrace): string {
  const d = trace.data as Record<string, unknown> | undefined
  if (!d) return ''
  const title = typeof d.title === 'string' ? d.title : ''
  const desc = typeof d.description === 'string' ? d.description : ''
  const kpis = d.kpis as Record<string, unknown> | undefined
  let html = '<div style="margin:6px 0 6px 16px;padding:8px 12px;background:#ecfdf5;border-left:3px solid #059669;border-radius:4px">'
  html += '<strong style="color:#059669">' + escapeHtml(safeValue(title)) + '</strong>'
  if (desc) html += '<div style="font-size:13px;color:#374151;margin-top:2px">' + escapeHtml(safeValue(desc)) + '</div>'
  if (kpis) {
    html += '<div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:6px">'
    const kpiKeys = Object.keys(kpis)
    for (let i = 0; i < kpiKeys.length; i++) {
      const kpiVal = kpis[kpiKeys[i]]
      if (isLargeBlob(kpiVal)) continue // skip encrypted / oversized KPI values
      html += '<span style="font-size:12px;background:#d1fae5;padding:2px 6px;border-radius:3px"><b>' + escapeHtml(kpiKeys[i]) + ':</b> ' + escapeHtml(safeValue(kpiVal)) + '</span>'
    }
    html += '</div>'
  }
  html += '</div>'
  return html
}

function buildHtmlSummary(
  session: TraceSession,
  endedAt: string,
  structured: StructuredTrace[],
  kpis: SessionKpis
): string {
  const events = structured.filter(isStructuredEvent)

  // --- Session header ---
  let html = '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
  html += '<title>Session Summary — ' + escapeHtml(session.userLogin ?? 'unknown') + '</title>'
  html += '<style>'
  html += 'body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;margin:0;padding:24px;background:#f9fafb;color:#111827}'
  html += '.card{background:#fff;border:1px solid #e5e7eb;border-radius:8px;padding:20px;margin-bottom:16px;box-shadow:0 1px 3px rgba(0,0,0,.06)}'
  html += '.kpi-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin:16px 0}'
  html += '.kpi-box{background:#f0f9ff;border:1px solid #bfdbfe;border-radius:6px;padding:12px;text-align:center}'
  html += '.kpi-box .value{font-size:24px;font-weight:700;color:#1d4ed8}'
  html += '.kpi-box .label{font-size:12px;color:#6b7280;margin-top:4px}'
  html += '.timeline{border-left:2px solid #d1d5db;margin-left:12px;padding-left:16px}'
  html += '.tl-item{position:relative;margin-bottom:10px;padding:4px 0}'
  html += '.tl-item::before{content:"";position:absolute;left:-22px;top:8px;width:10px;height:10px;border-radius:50%;background:#d1d5db;border:2px solid #fff}'
  html += '.tl-item.ask::before{background:#d97706}'
  html += '.tl-item.feedback::before{background:#7c3aed}'
  html += '.tl-item.award::before{background:#059669}'
  html += '.time{font-size:11px;color:#9ca3af}'
  html += 'h1{margin:0 0 4px 0;font-size:22px}'
  html += 'h2{margin:24px 0 8px 0;font-size:18px;color:#374151}'
  html += 'h3{margin:0 0 6px 0;font-size:15px}'
  html += '.tag{display:inline-block;padding:1px 6px;border-radius:3px;font-size:12px;background:#e5e7eb;color:#374151;margin-right:4px}'
  html += '.no-solution{color:#dc2626;font-style:italic;font-size:13px}'
  html += '@media print{body{padding:12px}.card{box-shadow:none;break-inside:avoid}}'
  html += '</style></head><body>'

  // Header
  html += '<div class="card">'
  html += '<h1>Session Summary</h1>'
  html += '<div style="color:#6b7280;font-size:14px">User: <b>' + escapeHtml(session.userLogin ?? 'unknown') + '</b> &middot; Session: <span style="font-family:monospace;font-size:12px">' + escapeHtml(session.sessionId) + '</span></div>'
  html += '<div style="color:#6b7280;font-size:13px;margin-top:4px">' + formatTime(session.startedAt) + ' &rarr; ' + formatTime(endedAt) + '</div>'
  html += '</div>'

  // KPIs
  html += '<div class="kpi-grid">'
  html += '<div class="kpi-box"><div class="value">' + formatMs(kpis.total_session_time_ms) + '</div><div class="label">Total Session Time</div></div>'
  html += '<div class="kpi-box"><div class="value">' + String(events.length) + '</div><div class="label">Events Handled</div></div>'

  const resolved = events.filter(function (e) { return e.decision_time_ms !== null })
  html += '<div class="kpi-box"><div class="value">' + resolved.length + ' / ' + events.length + '</div><div class="label">Assistance relevance</div></div>'
  html += '<div class="kpi-box"><div class="value">' + formatMs(kpis.avg_decision_time_ms) + '</div><div class="label">Avg Decision Time (across all events)</div></div>'
  html += '</div>'

  // Per-event details
  html += '<h2>Event Details</h2>'
  for (let ei = 0; ei < events.length; ei++) {
    const evt = events[ei]
    const d = evt.data as Record<string, unknown> | undefined
    const meta = (d?.metadata ?? {}) as Record<string, unknown>
    const eventType = typeof meta.event_type === 'string' ? normalizeEventType(meta.event_type) : 'Unknown'
    const eventId = typeof meta.id_event === 'string' ? meta.id_event : String(meta.id_event ?? '')
    const eventTitle = typeof d?.title === 'string' ? d.title : ''
    const eventSummary = typeof d?.summary === 'string' ? d.summary : ''

    html += '<div class="card">'
    html += '<h3>' + stepBadge('EVENT') + ' Event #' + (ei + 1)
    if (eventId) html += ' <span class="tag">ID: ' + escapeHtml(eventId) + '</span>'
    html += ' <span class="tag">' + escapeHtml(eventType) + '</span>'
    html += '</h3>'
    if (eventTitle) html += '<div style="font-size:15px;font-weight:600;margin:4px 0">' + escapeHtml(eventTitle) + '</div>'
    if (eventSummary) html += '<div style="font-size:13px;color:#6b7280;margin-bottom:4px">' + escapeHtml(eventSummary) + '</div>'
    html += '<div class="time">' + formatTime(evt.date) + '</div>'
    html += eventMetadataHtml(evt.data)
    html += cognitiveSnapshotHtml(evt.data)

    // Decision time
    if (evt.decision_time_ms !== null) {
      html += '<div style="margin-top:8px;font-size:13px">&#9201; Decision time: <b>' + formatMs(evt.decision_time_ms) + '</b></div>'
    } else {
      html += '<div class="no-solution" style="margin-top:8px">No solution selected</div>'
    }

    // Timeline of interactions
    if (evt.interactions.length > 0) {
      html += '<div style="margin-top:10px;font-size:13px;color:#6b7280;font-weight:600">Interactions</div>'
      html += '<div class="timeline">'
      for (let ii = 0; ii < evt.interactions.length; ii++) {
        const inter = evt.interactions[ii]
        const cls = inter.step === 'ASKFORHELP' ? 'ask' : inter.step === 'FEEDBACK' ? 'feedback' : inter.step === 'AWARD' ? 'award' : ''
        html += '<div class="tl-item ' + cls + '">'
        html += stepBadge(inter.step) + ' <span class="time">' + formatTime(inter.date) + '</span>'
        if (inter.step === 'FEEDBACK') {
          html += '<div style="margin-top:2px;font-size:13px">' + feedbackLabel(inter.data) + '</div>'
        } else if (inter.step === 'AWARD') {
          html += awardHtml(inter)
        }
        html += cognitiveSnapshotHtml(inter.data)
        html += '</div>'
      }
      html += '</div>'
    }

    html += '</div>'
  }

  html += '</body></html>'
  return html
}

function download(content: string, mimeType: string, fileName: string) {
  const blob = new Blob([content], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = fileName
  document.body.appendChild(anchor)
  anchor.click()
  anchor.remove()
  URL.revokeObjectURL(url)
}

function sessionFileName(session: TraceSession, extension: 'json' | 'csv' | 'html') {
  const started = session.startedAt.replace(/:/g, '-').replace('.', '-')
  const user = session.userLogin ?? 'unknown'
  return `historic-session-${user}-${started}.${extension}`
}

export function startTraceSession(userLogin?: string) {
  saveSession(createSession(userLogin))
}

export async function recordTraceForSession(
  trace: { step: SessionStep; use_case: Trace['use_case']; data: unknown; date?: string }
) {
  const session = loadSession() ?? createSession()

  if (trace.step === 'EVENT') {
    // Skip pre-existing cards from the initial SSE sync.
    // Compare publishDate (real wall-clock time) against session start.
    // start_date is simulation time and can be in the future, so it's not reliable.
    const traceData = trace.data as Record<string, unknown> | undefined
    const pubDate = traceData?.publish_date as string | undefined
    if (pubDate) {
      const cardPublishTime = new Date(pubDate).getTime()
      const sessionTime = new Date(session.startedAt).getTime()
      if (cardPublishTime < sessionTime) return
    }

    const key = eventKey(trace.data)
    if (key) {
      const alreadyRecorded = session.traces.some(
        (item) => item.step === 'EVENT' && eventKey(item.data) === key
      )
      if (alreadyRecorded) return
    }
  }

  // Enrich trace data with the latest cognitive snapshot — but only when the
  // operator has consented. Without consent, nothing is fetched or recorded.
  // On API failure the snapshot contains an `error` field.
  let enrichedData: unknown = trace.data
  if (hasCognitiveConsent()) {
    try {
      const cognitiveSnapshot = await fetchCognitiveSnapshot()
      const base = (trace.data !== null && typeof trace.data === 'object')
        ? (trace.data as Record<string, unknown>)
        : {}
      enrichedData = { ...base, cognitive_snapshot: cognitiveSnapshot }
    } catch (err: unknown) {
      // Should not happen (fetchCognitiveSnapshot never throws), but guard anyway
      const message = err instanceof Error ? err.message : String(err)
      const base = (trace.data !== null && typeof trace.data === 'object')
        ? (trace.data as Record<string, unknown>)
        : {}
      enrichedData = {
        ...base,
        cognitive_snapshot: {
          cognitive_performance: null,
          stress_state: null,
          cognitive_performance_explainability: null,
          stress_explainability: null,
          error: `Failed to get cognitive factors: ${message}`
        }
      }
    }
  }

  session.traces.push({
    date: trace.date ? String(trace.date) : new Date().toISOString(),
    use_case: trace.use_case,
    step: trace.step,
    data: enrichedData
  })
  saveSession(session)
}

export function exportTraceSession(format: ExportFormat = 'json', options: ExportOptions = {}) {
  const force = options.force ?? false
  const session = loadSession() ?? (force ? createSession(options.userLogin) : undefined)
  if (!session) return
  if (!force && session.traces.length === 0) return

  const endedAt = new Date().toISOString()

  if (format === 'csv') {
    const csv = buildCsv(session, endedAt)
    download(csv, 'text/csv;charset=utf-8', sessionFileName(session, 'csv'))
    return
  }

  const structured = buildStructuredTraces(session.traces)

  // Normalize event_type in metadata for JSON export (e.g. 'KPI' → 'Overload')
  for (let i = 0; i < structured.length; i++) {
    const t = structured[i]
    if (t.step === 'EVENT') {
      const d = t.data as Record<string, unknown> | undefined
      const meta = d?.metadata as Record<string, unknown> | undefined
      if (meta && typeof meta.event_type === 'string') {
        meta.event_type = normalizeEventType(meta.event_type)
      }
    }
  }

  // --- Session-level KPIs ---
  const totalSessionTimeMs = new Date(endedAt).getTime() - new Date(session.startedAt).getTime()
  const events = structured.filter(isStructuredEvent)
  const totalEvents = events.length
  const sumDecisionTime = events.reduce(
    (sum, evt) => sum + (evt.decision_time_ms ?? 0),
    0
  )
  const kpis: SessionKpis = {
    total_session_time_ms: totalSessionTimeMs,
    avg_decision_time_ms: totalEvents > 0 ? sumDecisionTime / totalEvents : null
  }

  // Build HTML summary before replacing event_context so the image is preserved in the HTML
  const summaryHtml = buildHtmlSummary(session, endedAt, structured, kpis)

  // Replace base64 event_context in metadata with a placeholder for the JSON export
  for (let i = 0; i < structured.length; i++) {
    const t = structured[i]
    if (t.step === 'EVENT') {
      const d = t.data as Record<string, unknown> | undefined
      const meta = d?.metadata as Record<string, unknown> | undefined
      if (meta && typeof meta.event_context === 'string' && isLargeBlob(meta.event_context)) {
        meta.event_context = 'base64 image, refer to the html file'
      }
    }
  }

  const json = JSON.stringify(
    {
      sessionId: session.sessionId,
      userLogin: session.userLogin,
      startedAt: session.startedAt,
      endedAt,
      kpis,
      traces: structured
    },
    null,
    2
  )
  download(json, 'application/json;charset=utf-8', sessionFileName(session, 'json'))

  // Open HTML summary in a new tab (use <a target="_blank"> to avoid popup blocker)
  const summaryBlob = new Blob([summaryHtml], { type: 'text/html;charset=utf-8' })
  const summaryUrl = URL.createObjectURL(summaryBlob)
  const summaryAnchor = document.createElement('a')
  summaryAnchor.href = summaryUrl
  summaryAnchor.target = '_blank'
  summaryAnchor.rel = 'noopener'
  document.body.appendChild(summaryAnchor)
  summaryAnchor.click()
  summaryAnchor.remove()
  // Also download the HTML file as a backup
  download(summaryHtml, 'text/html;charset=utf-8', sessionFileName(session, 'html'))
}

export function clearTraceSession() {
  localStorage.removeItem(STORAGE_KEY)
}
