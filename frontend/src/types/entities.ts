import { Entities as config, type EntitiesTypes } from '@/entities/config'

export const Entities = config

export const EntitiesArray = Object.keys(Entities) as (keyof typeof Entities)[]

export type Entity = keyof typeof Entities

export type Metadata<T extends Entity = Entity> = EntitiesTypes[T]['Metadata']
export type Context<T extends Entity = Entity> = EntitiesTypes[T]['Context']
export type Action<T extends Entity = Entity> = EntitiesTypes[T]['Action']
