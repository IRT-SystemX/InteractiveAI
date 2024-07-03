import { ENTITIES_CONFIG as config, type EntitiesTypes } from '@/entities/config'

export const ENTITIES_CONFIG = config
Object.freeze(ENTITIES_CONFIG)

export const ENTITIES = Object.keys(ENTITIES_CONFIG) as (keyof typeof ENTITIES_CONFIG)[]
Object.freeze(ENTITIES)

export type Entity = keyof typeof ENTITIES_CONFIG

export type AppData<E extends Entity = Entity> = EntitiesTypes[E] extends { AppData: unknown }
  ? EntitiesTypes[E]['AppData']
  : any
export type Metadata<E extends Entity = Entity> = EntitiesTypes[E]['Metadata']
export type Context<E extends Entity = Entity> = EntitiesTypes[E]['Context']
export type Action<E extends Entity = Entity> = EntitiesTypes[E]['Action']
export type TaskTypes<E extends Entity = Entity> = EntitiesTypes[E] extends { TaskTypes: unknown }
  ? EntitiesTypes[E]['TaskTypes']
  : any
