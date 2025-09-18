import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// 修改为你的后端地址/端口
const backend = 'http://localhost:8000'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // 如前端走 /api 开头的请求，则代理到 FastAPI，避免 CORS
      // 开启方式：把前端基地址改为 /api（或直接在 axios 里用 /api）
      // '/api': { target: backend, changeOrigin: true, secure: false }
    },
  },
})
