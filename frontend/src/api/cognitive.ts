/**
 * Client for the INESCTEC InteractiveAI cognitive API.
 * Fetches per-event, per-agent cognitive state factors and returns a
 * structured snapshot that is attached to every session-trace entry.
 *
 * Requests are routed through the nginx proxy at /cognitive-api/ to avoid
 * browser CORS restrictions when calling https://wesenss.inesctec.pt directly.
 *
 * Hardcoded values (event_id = 885, first agent from the list) are used
 * until the dynamic event → cognitive-event mapping is in place.
 */

// Routed through nginx /cognitive-api/ → https://wesenss.inesctec.pt/api/v1/
const COGNITIVE_BASE_URL = '/cognitive-api'

// Injected at build time via VITE_COGNITIVE_TOKEN env var (never commit the token)
const COGNITIVE_TOKEN = import.meta.env.VITE_COGNITIVE_TOKEN ?? ''

// Hardcoded until dynamic event_id resolution is implemented
const DEFAULT_EVENT_ID = 885

const FACTOR_IDS = {
  COGNITIVE_PERFORMANCE: '105',
  STRESS_STATE: '106',
  COGNITIVE_PERFORMANCE_EXPLAINABILITY: '107',
  STRESS_EXPLAINABILITY: '108'
} as const

// --------------------------------------------------------------------------
// Public types
// --------------------------------------------------------------------------

export type CognitiveFactorEntry = {
  value: string
  timestamp: string
}

export type CognitiveSnapshot = {
  /** Numeric cognitive-performance score (factor 105) */
  cognitive_performance: CognitiveFactorEntry | null
  /** Stress state: value "1" = stressed, "0" = not stressed (factor 106) */
  stress_state: CognitiveFactorEntry | null
  /** Free-text explanation of the cognitive-performance score (factor 107) */
  cognitive_performance_explainability: CognitiveFactorEntry | null
  /** Free-text explanation of the stress state (factor 108) */
  stress_explainability: CognitiveFactorEntry | null
  /** Set when the API call failed — contains the error message */
  error?: string
}

// --------------------------------------------------------------------------
// Internal helpers
// --------------------------------------------------------------------------

type LatestDataItem = {
  agent_id: string
  factor_id: string
  literal_id: string
  data: string
  factor_timestamp: string
}

async function cognitiveGet<T>(path: string): Promise<T> {
  const response = await fetch(`${COGNITIVE_BASE_URL}${path}`, {
    headers: { Authorization: `Bearer ${COGNITIVE_TOKEN}` }
  })
  if (!response.ok) throw new Error(`Cognitive API ${response.status}: ${path}`)
  return response.json() as Promise<T>
}

// --------------------------------------------------------------------------
// Public API
// --------------------------------------------------------------------------

/**
 * Fetch a cognitive snapshot for the given event:
 *  1. Retrieve the agent list for the event.
 *  2. Fetch the latest factor data for the first agent.
 *  3. Extract factors 105 / 106 / 107 / 108.
 *
 * Always returns a CognitiveSnapshot object. On failure the `error` field is
 * populated with the reason so callers can surface it in logs and exports.
 */
export async function fetchCognitiveSnapshot(
  eventId: number = DEFAULT_EVENT_ID
): Promise<CognitiveSnapshot> {
  const empty: CognitiveSnapshot = {
    cognitive_performance: null,
    stress_state: null,
    cognitive_performance_explainability: null,
    stress_explainability: null
  }
  try {
    // Step 1 — get agents for this event
    const agentData = await cognitiveGet<{ agents: Array<{ id: string }> }>(
      `/agent_event/list/${eventId}`
    )
    const agents = agentData.agents ?? []
    if (agents.length === 0) {
      return { ...empty, error: `No agents found for event ${eventId}` }
    }

    const agentId = agents[0].id

    // Step 2 — get latest data for the first agent
    const latestData = await cognitiveGet<{ event_id: string; latest_data: LatestDataItem[] }>(
      `/event_product/latest_data_agent/${eventId}/${agentId}`
    )
    const items: LatestDataItem[] = latestData.latest_data ?? []

    const find = (factorId: string): CognitiveFactorEntry | null => {
      const item = items.find((i) => i.factor_id === factorId)
      return item ? { value: item.data, timestamp: item.factor_timestamp } : null
    }

    return {
      cognitive_performance: find(FACTOR_IDS.COGNITIVE_PERFORMANCE),
      stress_state: find(FACTOR_IDS.STRESS_STATE),
      cognitive_performance_explainability: find(FACTOR_IDS.COGNITIVE_PERFORMANCE_EXPLAINABILITY),
      stress_explainability: find(FACTOR_IDS.STRESS_EXPLAINABILITY)
    }
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err)
    return { ...empty, error: `Failed to get cognitive factors: ${message}` }
  }
}
