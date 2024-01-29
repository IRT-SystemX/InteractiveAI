import type { Severity } from '../cards'

export type Node = {
  id: number
  selected: boolean
  status: ('active' | Severity)[]
  x?: number
  y?: number
  fx?: number | null
  fy?: number | null
}

export type Link = {
  source: number | Node
  target: number | Node
  rank: number
  data: [string, number][]
}
