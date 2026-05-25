import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Bind on all interfaces so a phone on the LAN (or a tunnel) can reach the
    // Vite dev server. `allowedHosts: true` permits Cloudflare/ngrok tunnel
    // hostnames (otherwise Vite rejects the Host header with a 403).
    host: true,
    allowedHosts: true,
  },
  optimizeDeps: {
    exclude: ['lucide-react'],
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: undefined,
      },
    },
  },
  base: '/',
});