// Import your theme here
import './RTE/assets/theme.scss'

// Import your types here
import type { RTE } from './RTE/types'

// Add your entity and config here
// darkMode: use dark mode
export const ENTITIES_CONFIG = {
  RTE: { darkMode: false }
} as const
Object.freeze(ENTITIES_CONFIG)

// Bind your types here
export type EntitiesTypes = {
  RTE: RTE
}
