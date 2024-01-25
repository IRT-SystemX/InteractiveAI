import type { Severity } from '@/types/cards'

/**
 * Get dynamic asset url
 * @param path Path string to the asset, relative to `src` folder
 * @returns Asset url
 */
export function asset(path: string) {
  return new URL(`../${path}`, import.meta.url).href
}

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
  }
}

export function minmax(value: number, max = 1, min = 0) {
  return Math.min(Math.max(min, value), max)
}

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

export function randomInt(min: number, max: number) {
  return Math.floor(Math.random() * (Math.floor(max) - Math.ceil(min) + 1)) + Math.ceil(min)
}

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

export function remove<T>(array: T[], comparison: (value: T, index: number, obj: T[]) => unknown) {
  const index = array.findIndex(comparison)
  if (index > -1) array.splice(index, 1)
  return array
}

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
