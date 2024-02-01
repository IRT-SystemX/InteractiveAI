import type * as DA from './entities/DA'
import type * as ORANGE from './entities/ORANGE'
import type * as RTE from './entities/RTE'
import type * as SNCF from './entities/SNCF'
// You can add your custom types here

export const Entities = <const>{
  ORANGE: { hydrated: true },
  DA: { hydrated: false },
  RTE: { hydrated: false },
  SNCF: { hydrated: true }
}

type EntitiesTypes = {
  DA: { Context: DA.Context; Metadata: DA.Metadata }
  ORANGE: { Context: ORANGE.Context; Metadata: ORANGE.Metadata }
  RTE: { Context: RTE.Context; Metadata: RTE.Metadata }
  SNCF: { Context: SNCF.Context; Metadata: SNCF.Metadata }
}

export const EntitiesArray = Object.keys(Entities)

export type Entity = keyof typeof Entities

export type Metadata<T extends Entity = Entity> = EntitiesTypes[T]['Metadata']

export type Context<T extends Entity = Entity> = EntitiesTypes[T]['Context']
