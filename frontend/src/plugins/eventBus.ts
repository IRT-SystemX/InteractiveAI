import mitt from 'mitt'

import type { Card } from '@/types/cards'
import type { CardMetadata } from '@/types/entities'

const eventBus = mitt<{
  'progress:start': void
  'progress:stop': void
  modal: string
  'assistant:selected': Card<CardMetadata>
  'graph:showTooltip': any
  'assistant:tab': number
  'assistant:procedure:checked': any
}>()

export default eventBus
