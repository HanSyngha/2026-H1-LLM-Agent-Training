import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/auth': 'http://localhost:47777',
      '/challenges': 'http://localhost:47777',
      '/completions': 'http://localhost:47777',
      '/reactions': 'http://localhost:47777',
      '/questions': 'http://localhost:47777',
      '/settings': 'http://localhost:47777',
      '/health': 'http://localhost:47777',
      '/browser-target': 'http://localhost:47777',
      '/api': 'http://localhost:47777',
    },
  },
})
