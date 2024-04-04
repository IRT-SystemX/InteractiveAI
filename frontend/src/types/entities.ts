import { Entities as config, type EntitiesTypes } from '@/entities/config'

export const Entities = config

export const EntitiesArray = Object.keys(Entities) as (keyof typeof Entities)[]

export type Entity = keyof typeof Entities

export type Metadata<E extends Entity = Entity> = EntitiesTypes[E]['Metadata']
export type Context<E extends Entity = Entity> = EntitiesTypes[E]['Context']
export type Action<E extends Entity = Entity> = EntitiesTypes[E]['Action']
export type TaskTypes<E extends Entity = Entity> = EntitiesTypes[E] extends { TaskTypes: unknown }
  ? EntitiesTypes[E]['TaskTypes']
  : undefined
