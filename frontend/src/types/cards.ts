import type { Entity, Metadata } from './entities'

export type Severity = 'ALARM' | 'ACTION' | 'COMPLIANT' | 'INFORMATION'

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
  processInstanceId: `${string}-${string}-${string}-${string}-${string}`
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
  id: `${Lowercase<T>}Process.${string}-${string}-${string}-${string}-${string}`
  state: string
  startDate: number
  hydrated: boolean
  data?: { metadata: Metadata<T> }
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
