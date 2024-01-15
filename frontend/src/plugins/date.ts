// @ts-ignore
import { format as formatFNS } from 'date-fns'
import { enUS, fr } from 'date-fns/locale'

const locales = { fr, en: enUS }

export const format = (date: number | Date, pattern: string) =>
  formatFNS(date, pattern, {
    // @ts-ignore
    locale:
      locales[
        (window.navigator.language.split('-')[0] ||
          import.meta.env.VITE_DEFAULT_LOCALE ||
          'en') as keyof typeof locales
      ]
  })
