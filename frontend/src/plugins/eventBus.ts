import mitt from 'mitt'

import type { Card } from '@/types/cards'
import type { UUID } from '@/types/formats'

const eventBus = mitt<{
  'progress:start': void
  'progress:stop': void
  'modal:open': {
    id?: UUID
    data: string
    type: 'choice' | 'info'
  }
  'modal:close': { id: UUID; res: 'ok' | 'ko' }
  'graph:update': any
  'graph:showTooltip': any
  'notifications:ended': Card
}>()

export default eventBus
