import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  test: {
    environment: 'happy-dom',
    globals: false,
    include: ['src/**/*.{test,spec}.{ts,js}'],
    coverage: {
      provider: 'v8',
      include: ['src/composables/**/*.ts', 'src/utils/**/*.ts', 'src/components/video/useVideoPlayer.ts'],
      reporter: ['text', 'html'],
      thresholds: {
        lines: 80,
      },
    },
  },
})