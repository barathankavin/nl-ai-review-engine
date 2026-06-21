import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  const sheetId =
    env.VITE_GOOGLE_SHEET_ID ?? '1BL-09eLm61Zy3OLFxxqQVLf-I148dC30qbaKWa618wI';
  const sheetGid = env.VITE_GOOGLE_SHEET_GID ?? '0';

  return {
    plugins: [react()],
    build: {
      outDir: 'dist',
      sourcemap: false,
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ['react', 'react-dom'],
          },
        },
      },
    },
    preview: {
      port: 4173,
      proxy: {
        '/api/v1': {
          target: env.VITE_API_PROXY_TARGET ?? 'http://127.0.0.1:8000',
          changeOrigin: true,
        },
      },
    },
    server: {
      proxy: {
        '/api/reviews.csv': {
          target: 'https://docs.google.com',
          changeOrigin: true,
          rewrite: () =>
            `/spreadsheets/d/${sheetId}/export?format=csv&gid=${sheetGid}`,
        },
        '/api/v1': {
          target: env.VITE_API_PROXY_TARGET ?? 'http://127.0.0.1:8000',
          changeOrigin: true,
        },
      },
    },
  };
});
