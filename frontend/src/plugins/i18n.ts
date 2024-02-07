import { nextTick } from 'vue'
import { createI18n } from 'vue-i18n'

import { EntitiesArray } from '@/entities/entities'
import en from '@/locales/en.json'
import fr from '@/locales/fr.json'

export const SUPPORT_LOCALES = ['en', 'fr'] as const

export default createI18n({
  locale: window.navigator.language.split('-')[0] || import.meta.env.VITE_DEFAULT_LOCALE || 'en',
  fallbackLocale: import.meta.env.VITE_FALLBACK_LOCALE || 'en',
  legacy: false,
  missingWarn: false,
  fallbackWarn: false,
  messages: {
    en,
    fr
  }
})

export async function setupEntitiesLocales(i18n: ReturnType<typeof createI18n>) {
  for (const entity of EntitiesArray)
    for (const locale of SUPPORT_LOCALES) {
      i18n.global.setLocaleMessage(
        `${locale}-${entity}`,
        (await import(`../entities/${entity}/locales/${locale}.json`)).default
      )
    }
  return nextTick()
}
