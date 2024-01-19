import type { Context, Entity } from './entities'

export type Recommendations = {
  actions: RecommendationAction[]
}

export type RecommendationAction = object

export type ContextResponse = [
  {
    data: Context
    date: `${number}-${number}-${number}T${number}:${number}:${number}.${number}`
    id_context: `${string}-${string}-${string}-${string}-${string}`
    use_case: Entity
  }
]
