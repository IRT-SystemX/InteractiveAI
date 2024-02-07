import 'modern-normalize/modern-normalize.css'
import './assets/css/main.scss'

import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import { createApp } from 'vue'

import App from './App.vue'
import i18n, { setupEntitiesLocales } from './plugins/i18n'
import router from './router'

const app = createApp(App)

const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)
app.use(pinia)

app.use(router)

await setupEntitiesLocales(i18n)
app.use(i18n)

app.mount('#app')
