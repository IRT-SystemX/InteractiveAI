import type { Entity } from './entities'

export type Context<T> = [
  {
    data: T
    date: `${number}-${number}-${number}T${number}:${number}:${number}.${number}`
    id_context: `${string}-${string}-${string}-${string}-${string}`
    use_case: Entity
  }
]
