import type * as DA from './entities/DA'
import type * as ORANGE from './entities/ORANGE'
import type * as RTE from './entities/RTE'
import type * as SNCF from './entities/SNCF'
// You can add your custom types here

export const Entities = <const>['ORANGE', 'DA', 'SNCF', 'RTE']

export type Entity = (typeof Entities)[number]

export type CardMetadata = DA.Metadata | ORANGE.Metadata | RTE.Metadata | SNCF.Metadata

export type Context = DA.Context | ORANGE.Context | RTE.Context | SNCF.Context
