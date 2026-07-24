/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API: string
  readonly VITE_DEFAULT_LOCALE: string
  readonly VITE_FALLBACK_LOCALE: string
  readonly VITE_POWERGRID_SIMU: string
  readonly VITE_RAILWAY_SIMU: string
  readonly VITE_ATM_SIMU: string
  readonly VITE_COGNITIVE_TOKEN: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
