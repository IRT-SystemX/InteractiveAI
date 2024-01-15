import mitt from 'mitt'

import type { Card } from '@/types/cards'

const eventBus = mitt<{
  'progress:start': void
  'progress:stop': void
  modal: string
  'assistant:selectedCard': Card
  'assistant:correlations': Card
  'graph:showTooltip': any
  'assistant:tab': number
  'assistant:procedure:checked': any
  'assistant:procedure:plan': void
}>()

export default eventBus
