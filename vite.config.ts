import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
export default defineConfig({
  plugins: [react()],
  cacheDir: '.vite-cache',
  resolve: { dedupe: ['react', 'react-dom', 'three'] },
  build: { rollupOptions: { output: { manualChunks: id => id.includes('/three/') ? 'three' : undefined } } }
});
