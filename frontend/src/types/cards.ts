import type { Entity, Metadata } from './entities'
import type { UUID } from './formats'

export const SEVERITIES = ['INFORMATION', 'COMPLIANT', 'ACTION', 'ALARM'] as const
Object.freeze(SEVERITIES)
export type Severity = (typeof SEVERITIES)[number]
export const CRITICALITIES = ['ND', 'ROUTINE', 'LOW', 'MEDIUM', 'HIGH'] as const
Object.freeze(CRITICALITIES)
export type Criticality = (typeof CRITICALITIES)[number]

type PublisherType = 'EXTERNAL' | 'ENTITY'

export enum CardOperationType {
  ADD = 'ADD',
  UPDATE = 'UPDATE',
  DELETE = 'DELETE',
  ACK = 'ACK'
}

export type Card<E extends Entity = Entity> = {
  data: {
    criticality: Criticality
    metadata: Metadata<E>
    parent_event_id: Card['processInstanceId'] | null
  }
  read?: boolean
  id: `${Card['process']}.${Card['processInstanceId']}`
  processInstanceId: UUID
  uid: string
  startDate: number
  endDate?: number
  creationDate?: number
  publishDate: number
  severity: Severity
  entityRecipients: [E]
  keepChildCards: boolean
  hasBeenAcknowledged?: boolean
  hasBeenRead?: boolean
  process: 'cabProcess'
  publisherType: PublisherType
  processVersion: '1'
  summary: {
    parameters: { summary: string }
    key: string
  }
  summaryTranslated: string
  title: { parameters: { title: string }; key: string }
  titleTranslated: string
  publisher: string
  processStateKey: `cabProcess.${string}`
  state: string
}

export type CardAck = {
  cardUid: string
  entitiesAcks: Entity[]
  type: CardOperationType.ACK
  cardId: string
}

export type CardDelete = {
  entityRecipientsIds: Entity[]
  type: CardOperationType.DELETE
  cardId: string
}

export type CardAdd<E extends Entity = Entity> = {
  entityRecipientsIds: Entity[]
  type: CardOperationType.ADD
  card: Card<E>
}

export type CardUpdate<E extends Entity = Entity> = {
  entityRecipientsIds: Entity[]
  type: CardOperationType.UPDATE
  card: Card<E>
}

export type CardEvent<E extends Entity = Entity> = CardAdd<E> | CardUpdate<E> | CardAck | CardDelete
