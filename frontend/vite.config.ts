import { fileURLToPath, URL } from 'node:url'

import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'
import istanbul from 'vite-plugin-istanbul'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    istanbul({
      cypress: true,
      include: 'src/**/*',
      exclude: ['node_modules'],
      extension: ['.js', '.ts', '.vue'],
      requireEnv: false,
      forceBuildInstrument: true
    })
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  envDir: 'env',
  build: {
    sourcemap: true
  },
  server: {
    watch: {
      ignored: ['**/coverage/**']
    }
  }
})
