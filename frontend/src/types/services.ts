import type { Context, Entity } from './entities'

export type Recommendations = {
  description: string
  title: string
  actions: RecommendationAction[]
}

export type RecommendationAction = { [key: string]: any }

export type ContextResponse<T extends Entity = Entity> = {
  data: Context<T>
  date: `${number}-${number}-${number}T${number}:${number}:${number}.${number}`
  id_context: `${string}-${string}-${string}-${string}-${string}`
  use_case: T
}[]
