import type { Criticality } from '@/types/cards'

export type Node = {
  id: number
  selected: boolean
  status: ('active' | Criticality)[]
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
