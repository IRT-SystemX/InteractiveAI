import type * as DA from './entities/DA'
import type * as ORANGE from './entities/ORANGE'
import type * as RTE from './entities/RTE'
import type * as SNCF from './entities/SNCF'
// You can add your custom types here

type EntityParams = { hydrated: boolean }

export const Entities: { [entity: string]: EntityParams } = <const>{
  ORANGE: { hydrated: true },
  DA: { hydrated: false },
  RTE: { hydrated: false },
  SNCF: { hydrated: true }
}

export const EntitiesArray = Object.keys(Entities)

export type Entity = keyof typeof Entities

export type CardMetadata = DA.Metadata | ORANGE.Metadata | RTE.Metadata | SNCF.Metadata

export type Context = DA.Context | ORANGE.Context | RTE.Context | SNCF.Context
