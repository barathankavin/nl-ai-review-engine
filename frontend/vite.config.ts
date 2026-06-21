import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  const sheetId =
    env.VITE_GOOGLE_SHEET_ID ?? '1BL-09eLm61Zy3OLFxxqQVLf-I148dC30qbaKWa618wI';
  const sheetGid = env.VITE_GOOGLE_SHEET_GID ?? '0';

  return {
    plugins: [react()],
    server: {
      proxy: {
        '/api/reviews.csv': {
          target: 'https://docs.google.com',
          changeOrigin: true,
          rewrite: () =>
            `/spreadsheets/d/${sheetId}/export?format=csv&gid=${sheetGid}`,
        },
      },
    },
  };
});
