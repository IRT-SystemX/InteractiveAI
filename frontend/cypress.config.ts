import coverage from '@cypress/code-coverage/task'
import { defineConfig } from 'cypress'

export default defineConfig({
  e2e: {
    specPattern: 'cypress/e2e/**/*.{cy,spec}.{js,jsx,ts,tsx}',
    baseUrl: 'http://localhost:4173',
    chromeWebSecurity: false,
    setupNodeEvents(on, config) {
      coverage(on, config)

      return config
    }
  }
})
