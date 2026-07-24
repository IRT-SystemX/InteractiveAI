/**
 * User consent for collecting and using cognitive/stress data.
 *
 * The operator is asked at login whether the platform may fetch their
 * cognitive and stress state. When consent is NOT given, cognitive data must
 * not be fetched, recorded in session traces, or sent to the AI agent.
 *
 * Backed by localStorage (single source of truth) so it can be read from both
 * Pinia stores and plain utility modules without creating circular imports.
 * The default — no stored value — is treated as "no consent", the safe default.
 */

const CONSENT_KEY = 'cognitiveConsent'

/** Record the operator's consent decision. */
export function setCognitiveConsent(value: boolean): void {
  localStorage.setItem(CONSENT_KEY, value ? 'true' : 'false')
}

/** True only when the operator has explicitly consented. */
export function hasCognitiveConsent(): boolean {
  return localStorage.getItem(CONSENT_KEY) === 'true'
}

/** Forget any previous decision (e.g. on logout) so the next login re-asks. */
export function clearCognitiveConsent(): void {
  localStorage.removeItem(CONSENT_KEY)
}
