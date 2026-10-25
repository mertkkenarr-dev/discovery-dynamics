import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  base: './', // göreli adresler: GitHub Pages alt yolunda (/discovery-dynamics/) da çalışır
  plugins: [react()],
  server: { port: 5297, strictPort: true },
})
