import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    port: 10073,
    open: true,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:10088',
        changeOrigin: true
      },
      '/uploads': {
        target: 'http://127.0.0.1:10088',
        changeOrigin: true
      }
    }
  }
})
