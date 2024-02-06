import type { Action, Context, Entity } from './entities'
import type { DateMillisecondsFormat, UUID } from './formats'

export type Recommendation<T extends Entity = Entity> = {
  agent_type: 'IA'
  use_case: Entity
  description: string
  title: string
  actions: Action<T>[]
}

export type ContextResponse<T extends Entity = Entity> = {
  data: Context<T>
  date: DateMillisecondsFormat
  id_context: UUID
  use_case: T
}[]
