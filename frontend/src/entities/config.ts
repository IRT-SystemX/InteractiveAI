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
export type EntitiesTypes = {
  DA: DA
  ORANGE: ORANGE
  RTE: RTE
  SNCF: SNCF
}
