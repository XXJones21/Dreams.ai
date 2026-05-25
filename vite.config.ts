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
    // Proxy the backend so the app + API are SAME-ORIGIN. The phone only needs
    // ONE tunnel (to Vite); /api (REST + WS) is forwarded to the FastAPI server
    // locally. No CORS config and no separate API origin/env var needed.
    // Override the target with VITE_API_PROXY_TARGET if the backend isn't on :8000.
    proxy: {
      '/api': {
        target: process.env.VITE_API_PROXY_TARGET || 'http://localhost:8000',
        changeOrigin: true,
        ws: true,
      },
      // ComfyUI image/video assets are served at http://127.0.0.1:8188/view?...
      // which a phone over the tunnel can't reach. Proxy them same-origin so the
      // frontend can rewrite asset URLs to /comfy/view?... (see api.ts mediaUrl).
      '/comfy': {
        target: process.env.VITE_COMFY_PROXY_TARGET || 'http://127.0.0.1:8188',
        changeOrigin: true,
        rewrite: (p) => p.replace(/^\/comfy/, ''),
      },
    },
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