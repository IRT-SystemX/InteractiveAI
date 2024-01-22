import type { CardMetadata, Entity } from './entities'

export type Severity = 'ALARM' | 'ACTION' | 'COMPLIANT' | 'INFORMATION'

type PublisherType = 'EXTERNAL' | 'ENTITY'

export enum CardOperationType {
  ADD = 'ADD',
  UPDATE = 'UPDATE',
  DELETE = 'DELETE',
  ACK = 'ACK'
}

export type Card<T extends CardMetadata> = {
  severity: Severity
  summary: {
    parameters: { summary: string }
    key: string
  }
  summaryTranslated: string
  keepChildCards: boolean
  hasBeenAcknowledged?: boolean
  processInstanceId: string
  process: string
  publisherType: PublisherType
  endDate: number
  publishDate: number
  processVersion: '1'
  title: { parameters: { title: string }; key: string }
  titleTranslated: string
  uid: string
  publisher: string
  entityRecipients: string[]
  id: string
  state: string
  startDate: number
  hydrated: boolean
  data?: { metadata: T }
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

export type CardAdd<T extends CardMetadata> = {
  entityRecipientsIds: Entity[]
  type: CardOperationType.ADD
  card: Card<T>
}

export type CardUpdate<T extends CardMetadata> = {
  entityRecipientsIds: Entity[]
  type: CardOperationType.UPDATE
  card: Card<T>
}

export type CardEvent<T extends CardMetadata> = CardAdd<T> | CardUpdate<T> | CardAck | CardDelete
