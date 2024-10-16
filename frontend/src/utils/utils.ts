import { useCardsStore } from '@/stores/cards'
import { type Card, CRITICALITIES, type Criticality } from '@/types/cards'
import type { UUID } from '@/types/formats'

/**
 * Get dynamic asset url
 * @param path Path string to the asset, relative to `src` folder
 * @returns Asset url
 */
export function asset(path: string) {
  return new URL(`../${path}`, import.meta.url).href
}

/**
 * Returns the standard color keyword for CSS styling associated to a criticality
 * @param criticality the criticality
 */
export function criticalityToColor(criticality: Criticality) {
  switch (criticality) {
    case 'HIGH':
      return 'error'
    case 'MEDIUM':
      return 'warning'
    case 'LOW':
      return 'success'
    case 'ROUTINE':
      return 'primary'
    case 'ND':
      return 'secondary'
  }
}

/**
 * Limits a value between min and max
 * @param value the value to clamp
 * @param max max value (default: 1)
 * @param min min value (default: 0)
 */
export function clamp(value: number, max = 1, min = 0) {
  return Math.min(Math.max(min, value), max)
}

/**
 * Calls function every interval, synced with time
 * eg: repeatEvery(fn, 60 * 1000) calls the function every minute at xx:00
 * @param callback the function to call
 * @param interval the interval
 */
export function repeatEvery(callback: () => void, interval: number) {
  // Check current time and calculate the delay until next interval
  const now = Date.now()
  const delay = interval - (now % interval)

  function start() {
    // Execute function now...
    callback()
    // ... and every interval
    setInterval(callback, interval)
  }

  // Delay execution until it's an even interval
  setTimeout(start, delay)
}

/**
 * Returns a random integer between min (ceiled) and max (floored)
 * @param min max value, floored if not an integer
 * @param max min value, ceiled if not an integer
 */
export function randomInt(min: number, max: number) {
  return Math.floor(Math.random() * (Math.floor(max) - Math.ceil(min) + 1)) + Math.ceil(min)
}

/**
 * Returns a unique color for a specific value
 * @param src a value to hash
 * @param lightness color's lightness
 * @param saturation color's saturation
 */
export function hashColor(src: string | number, lightness = 66, saturation = 100) {
  src = src.toString(2)
  let hash = 0
  for (let i = 0; i < src.length; i += 1) {
    hash = src.charCodeAt(i) + ((hash << 5) - hash)
    hash &= hash
  }
  return `hsl(${hash % 360}, ${saturation}%, ${lightness}%)`
}

/**
 * Removes in place the first value that matches from an array
 * @param array the array
 * @param comparison the comparison function to find the value to remove
 */
export function remove<T>(array: T[], comparison: (value: T, index: number, obj: T[]) => unknown) {
  const index = array.findIndex(comparison)
  if (index > -1) array.splice(index, 1)
  return array
}

/**
 * Adds or updates in place a value in an array
 * @param array the array
 * @param value the value to add
 * @param comparison the comparison function to find if the value already exists
 */
export function addOrUpdate<T>(
  array: T[],
  value: T,
  comparison: (value: T, index: number, obj: T[]) => unknown
) {
  const index = array.findIndex(comparison)
  if (index > -1) array.splice(index, 1, value)
  else array.push(value)
  return array
}

/**
 * Generates a universally unique identifier (UUID).
 *
 * @return {UUID} The generated UUID.
 */
export function uuid() {
  return window.isSecureContext
    ? crypto.randomUUID()
    : ('10000000-1000-4000-8000-100000000000'.replace(/[018]/g, (c) =>
        (+c ^ (crypto.getRandomValues(new Uint8Array(1))[0] & (15 >> (+c / 4)))).toString(16)
      ) as UUID)
}

/**
 * Returns the maximum criticality of the given cards, excluding those that have not been acknowledged if specified.
 *
 * @param {Criticality} [minimum='ND'] - The minimum criticality to consider. Defaults to 'ND'.
 * @param {Card[]} cards - The array of cards to find the maximum criticality from. Defaults to non-acknowledged cards.
 * @return {Criticality} The maximum criticality of the given cards.
 */
export function maxCriticality(
  minimum: Criticality = 'ND',
  cards: Card[] = useCardsStore()._cards.filter((card) => !card.hasBeenAcknowledged)
) {
  return cards.reduce(
    (prev: Criticality, curr) =>
      CRITICALITIES.indexOf(curr.data.criticality) > CRITICALITIES.indexOf(prev)
        ? curr.data.criticality
        : prev,
    minimum
  )
}

/**
 * Retrieves the value of a CSS variable from the document's body.
 *
 * @param {string} variable - The name of the CSS variable to retrieve.
 * @return {string} The value of the CSS variable, or an empty string if it is not found.
 */
export const getCSSVariable = (variable: string) =>
  getComputedStyle(document.body).getPropertyValue(`--${variable}`)

/**
 * Returns the root card of a given card by traversing up the parent_event_id chain.
 *
 * @param {Card} card - The card from which to start the traversal.
 * @return {Card} The root card of the given card.
 */
export function getRootCard(card: Card) {
  const cardsStore = useCardsStore()
  let curr = card
  while (card?.data.parent_event_id) {
    const parent = cardsStore._cards.find(
      (card) => card.processInstanceId === curr?.data.parent_event_id
    )
    if (!parent) break
    curr = parent
  }
  return curr
}
