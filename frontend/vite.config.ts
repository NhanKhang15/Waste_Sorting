import { resolve } from 'node:path'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  build: {
    rollupOptions: {
      // Use a named HTML entry to avoid a Windows/Rolldown path bug where
      // the absolute index.html path is treated as an emitted chunk name.
      input: {
        app: resolve(__dirname, 'index.html'),
      },
      output: {
        manualChunks(id) {
          if (id.includes('react-d3-tree') || id.includes('d3-')) return 'vendor-d3';
          if (id.includes('react-syntax-highlighter') || id.includes('refractor') || id.includes('prismjs')) return 'vendor-syntax-hl';
          if (id.includes('node_modules')) return 'vendor';
        },
      },
    },
  },
})
