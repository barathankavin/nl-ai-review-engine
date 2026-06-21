/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_GOOGLE_SHEET_ID: string;
  readonly VITE_GOOGLE_SHEET_GID: string;
  readonly VITE_REVIEWS_CSV_URL: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
