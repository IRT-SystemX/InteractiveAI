import mitt from 'mitt'

import type { Card } from '@/types/cards'
import type { Entity } from '@/types/entities'

const eventBus = mitt<
  {
    'progress:start': void
    'progress:stop': void
    'modal:open': {
      id?: `${string}-${string}-${string}-${string}-${string}`
      data: string
      type: 'choice' | 'info'
    }
    'modal:close': { id: `${string}-${string}-${string}-${string}-${string}`; res: 'ok' | 'ko' }
    'tabs:selected': number
    'graph:update': any
    'graph:showTooltip': any
    'assistant:tab': number
    'assistant:procedure:checked': any
  } & {
    [key in Entity as `assistant:selected:${key}`]: Card<key>
  }
>()

export default eventBus
