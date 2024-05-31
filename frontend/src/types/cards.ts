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
  severity: Severity
  summary: {
    parameters: { summary: string }
    key: string
  }
  summaryTranslated: string
  keepChildCards: boolean
  hasBeenAcknowledged?: boolean
  hasBeenRead?: boolean
  processInstanceId: UUID
  process: `${Lowercase<E>}Process`
  publisherType: PublisherType
  endDate: number
  publishDate: number
  processVersion: '1'
  title: { parameters: { title: string }; key: string }
  titleTranslated: string
  uid: string
  publisher: string
  entityRecipients: [E]
  id: `${Card['process']}.${Card['processInstanceId']}`
  state: string
  startDate: number
  data: {
    criticality: Criticality
    metadata: Metadata<E>
    parent_event_id: Card['processInstanceId']
  }
  read?: boolean
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
