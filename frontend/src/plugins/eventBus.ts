import mitt from 'mitt'

import type { Card } from '@/types/cards'

const eventBus = mitt<{
  'graph:update': any
  'graph:showTooltip': any
  'notifications:ended': Card
}>()

export default eventBus
