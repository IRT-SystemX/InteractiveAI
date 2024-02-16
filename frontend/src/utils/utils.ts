import type { Severity } from '@/types/cards'
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
 * Returns the standard color keyword for CSS styling associated to a severity
 * @param severity the severity
 */
export function severityToColor(severity: Severity) {
  switch (severity) {
    case 'ALARM':
      return 'error'
    case 'ACTION':
      return 'warning'
    case 'INFORMATION':
      return 'success'
    case 'COMPLIANT':
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
  return `hsl(${
    hash % 360
  }, ${saturation}%, calc(var(--lightness) + var(--lightness-factor) * ${lightness}%))`
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

export function uuid() {
  return '10000000-1000-4000-8000-100000000000'.replace(/[018]/g, (c) =>
    (+c ^ (crypto.getRandomValues(new Uint8Array(1))[0] & (15 >> (+c / 4)))).toString(16)
  ) as UUID
}
