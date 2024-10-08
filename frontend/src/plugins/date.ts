import { format as formatFNS } from 'date-fns'
import { enUS, fr } from 'date-fns/locale'

const LOCALES = { fr, en: enUS }
Object.freeze(LOCALES)

export const format = (date: number | Date, pattern: string) =>
  formatFNS(date, pattern, {
    locale:
      LOCALES[
        (window.navigator.language.split('-')[0] ||
          import.meta.env.VITE_DEFAULT_LOCALE ||
          'en') as keyof typeof LOCALES
      ]
  })
