import { type DA } from './entities/DA'
import { type ORANGE } from './entities/ORANGE'
import { type RTE } from './entities/RTE'
import { type SNCF } from './entities/SNCF'
// You can add your custom types here

export const Entities = <const>{
  ORANGE: { hydrated: true },
  DA: { hydrated: false },
  RTE: { hydrated: false },
  SNCF: { hydrated: true }
}

type EntitiesTypes = {
  DA: DA
  ORANGE: ORANGE
  RTE: RTE
  SNCF: SNCF
}

export const EntitiesArray = Object.keys(Entities) as (keyof typeof Entities)[]

export type Entity = keyof typeof Entities

export type Metadata<T extends Entity = Entity> = EntitiesTypes[T]['Metadata']

export type Context<T extends Entity = Entity> = EntitiesTypes[T]['Context']
