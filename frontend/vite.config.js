import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { viteSingleFile } from 'vite-plugin-singlefile'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  return {
    plugins: [
      vue(),
      viteSingleFile(),
    ],
    define: {
      // Expose env var to the app at build time
      'import.meta.env.VITE_API_BASE': JSON.stringify(env.VITE_API_BASE || ''),
    },
    build: {
      target: 'esnext',
      assetsInlineLimit: 100000000,
      chunkSizeWarningLimit: 100000000,
      rollupOptions: {
        output: {
          inlineDynamicImports: true,
        }
      }
    }
  }
})
