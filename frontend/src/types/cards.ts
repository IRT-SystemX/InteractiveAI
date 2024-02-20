import type { Entities, Entity, Metadata } from './entities'
import type { UUID } from './formats'

export const SeverityArray = ['ALARM', 'ACTION', 'COMPLIANT', 'INFORMATION', 'ND'] as const
export type Severity = (typeof SeverityArray)[number]

type PublisherType = 'EXTERNAL' | 'ENTITY'

export enum CardOperationType {
  ADD = 'ADD',
  UPDATE = 'UPDATE',
  DELETE = 'DELETE',
  ACK = 'ACK'
}

export type Card<T extends Entity = Entity> = {
  severity: Severity
  summary: {
    parameters: { summary: string }
    key: string
  }
  summaryTranslated: string
  keepChildCards: boolean
  hasBeenAcknowledged?: boolean
  processInstanceId: UUID
  process: `${Lowercase<T>}Process`
  publisherType: PublisherType
  endDate: number
  publishDate: number
  processVersion: '1'
  title: { parameters: { title: string }; key: string }
  titleTranslated: string
  uid: string
  publisher: string
  entityRecipients: [T]
  id: `${Lowercase<T>}Process.${UUID}`
  idMainEvent?: `${Lowercase<T>}Process.${UUID}`
  state: string
  startDate: number
  data: (typeof Entities)[T]['hydrated'] extends true
    ? { metadata: Metadata<T> }
    : { metadata: Metadata<T> } | undefined
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

export type CardAdd<T extends Entity = Entity> = {
  entityRecipientsIds: Entity[]
  type: CardOperationType.ADD
  card: Card<T>
}

export type CardUpdate<T extends Entity = Entity> = {
  entityRecipientsIds: Entity[]
  type: CardOperationType.UPDATE
  card: Card<T>
}

export type CardEvent<T extends Entity = Entity> = CardAdd<T> | CardUpdate<T> | CardAck | CardDelete
