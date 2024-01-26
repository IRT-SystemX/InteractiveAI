import { createI18n } from 'vue-i18n'

import en from '@/locales/en/en.json'
import enDA from '@/locales/en/en-DA.json'
import enORANGE from '@/locales/en/en-ORANGE.json'
import enRTE from '@/locales/en/en-RTE.json'
import enSNCF from '@/locales/en/en-SNCF.json'
import fr from '@/locales/fr/fr.json'
import frDA from '@/locales/fr/fr-DA.json'
import frORANGE from '@/locales/fr/fr-ORANGE.json'
import frRTE from '@/locales/fr/fr-RTE.json'
import frSNCF from '@/locales/fr/fr-SNCF.json'

export default createI18n({
  locale: window.navigator.language.split('-')[0] || import.meta.env.VITE_DEFAULT_LOCALE || 'en',
  fallbackLocale: import.meta.env.VITE_FALLBACK_LOCALE || 'en',
  legacy: false,
  missingWarn: false,
  fallbackWarn: false,
  messages: {
    en,
    'en-DA': enDA,
    'en-ORANGE': enORANGE,
    'en-RTE': enRTE,
    'en-SNCF': enSNCF,
    fr,
    'fr-DA': frDA,
    'fr-ORANGE': frORANGE,
    'fr-RTE': frRTE,
    'fr-SNCF': frSNCF
  }
})
