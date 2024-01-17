import mitt from 'mitt'

import type { Card } from '@/types/cards'

const eventBus = mitt<{
  'progress:start': void
  'progress:stop': void
  modal: string
  'assistant:selected': Card
  'graph:showTooltip': any
  'assistant:tab': number
  'assistant:procedure:checked': any
}>()

export default eventBus
