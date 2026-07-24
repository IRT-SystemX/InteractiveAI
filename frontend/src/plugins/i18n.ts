import { nextTick } from 'vue'
import { createI18n } from 'vue-i18n'

import en from '@/locales/en.json'
import fr from '@/locales/fr.json'
import { ENTITIES } from '@/types/entities'

export const SUPPORT_LOCALES = ['en', 'fr'] as const
Object.freeze(SUPPORT_LOCALES)

const i18n = createI18n({
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

export default i18n

export async function setupEntitiesLocales(instance: typeof i18n = i18n) {
  for (const entity of ENTITIES)
    for (const locale of SUPPORT_LOCALES) {
      instance.global.setLocaleMessage(
        `${locale}-${entity}`,
        (await import(`../entities/${entity}/locales/${locale}.json`)).default
      )
    }
  return nextTick()
}
