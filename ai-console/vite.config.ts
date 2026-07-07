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
  // Per .omc/specs/deep-interview-photo-videos-archive.md:
  // 统一在 /home/daxiong/code/console/data/ 下管理所有 media（图片 + 视频）。
  // publicDir 同时包含 `public/` (前端公共资源如 icons/admin.jpg) 和
  // `../../data/monitoring/` (算法输入源视频)，这样前端 `/monitoring/device_X.mp4`
  // URL 直接由 vite serve，无需 ai-console/public/ 软链。
  publicDir: [
    'public',
    resolve(__dirname, '../../data/monitoring'),
  ],
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
      // traffic-api HLS endpoint: traffic-api 路由固定是 /stream/{token}/.../{file}
      // → 转发时**保留 /stream 前缀**（之前误把 /stream 剥掉导致 traffic-api 404）
      '/stream': {
        target: 'http://127.0.0.1:10000',
        changeOrigin: true,
        configure: (proxy) => {
          proxy.on('proxyRes', fixMtxCookies)
        },
      },
      // 注：旧的 device-前缀代理条目已删除，traffic-api 端 HLS 统一在 /stream 下。
    }
  }
})
