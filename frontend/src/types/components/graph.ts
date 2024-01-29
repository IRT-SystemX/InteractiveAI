import type { Severity } from '../cards'

export type Node = { id: number; selected: boolean; status: ('active' | Severity)[] }

export type Link = { source: number; target: number; rank: number; data: [string, number][] }
