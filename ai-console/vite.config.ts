import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

function fixMtxCookies(proxyRes: any) {
  const cookies = proxyRes.headers['set-cookie']
  if (cookies) {
    proxyRes.headers['set-cookie'] = cookies.map((cookie: string) => {
      const withoutSecure = cookie.replace(/; Secure/gi, '')
      const withoutPartitioned = withoutSecure.replace(/; Partitioned/gi, '')
      const withSameSite = withoutPartitioned.replace(/; SameSite=None/gi, '; SameSite=Lax')
      const withPath = /;\s*path=/i.test(withSameSite) ? withSameSite : `${withSameSite}; Path=/`
      return withPath
    })
  }
}

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    port: 10073,
    host: true,
    open: true,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:10088',
        changeOrigin: true
      },
      '/uploads': {
        target: 'http://127.0.0.1:10088',
        changeOrigin: true
      },
      // traffic-api HLS endpoint: traffic-api 端 FFmpeg 输出 HLS 在此路径下
      '/stream': {
        target: 'http://127.0.0.1:10000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/stream/, ''),
        configure: (proxy) => {
          proxy.on('proxyRes', fixMtxCookies)
        },
      },
      // 注：旧的 device-前缀代理条目已删除，traffic-api 端 HLS 统一在 /stream 下。
    }
  }
})
