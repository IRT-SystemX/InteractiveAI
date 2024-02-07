// Import your theme here
import './DA/assets/theme.scss'
import './ORANGE/assets/theme.scss'
import './RTE/assets/theme.scss'
import './SNCF/assets/theme.scss'

// Import your types here
import type { DA } from './DA/types'
import type { ORANGE } from './ORANGE/types'
import type { RTE } from './RTE/types'
import type { SNCF } from './SNCF/types'

// Add your entity and config here
// hydrated: automatically fetch metadata for cards
// darkMode: use dark mode
export const Entities = <const>{
  DA: { hydrated: false, darkMode: true },
  ORANGE: { hydrated: true, darkMode: false },
  RTE: { hydrated: false, darkMode: false },
  SNCF: { hydrated: true, darkMode: false }
}

// Bind your types here
type EntitiesTypes = {
  DA: DA
  ORANGE: ORANGE
  RTE: RTE
  SNCF: SNCF
}

// Nothing to do here, types are automatically
// inferred from what you typed above
export const EntitiesArray = Object.keys(Entities) as (keyof typeof Entities)[]

export type Entity = keyof typeof Entities

export type Metadata<T extends Entity = Entity> = EntitiesTypes[T]['Metadata']
export type Context<T extends Entity = Entity> = EntitiesTypes[T]['Context']
export type Action<T extends Entity = Entity> = EntitiesTypes[T]['Action']
