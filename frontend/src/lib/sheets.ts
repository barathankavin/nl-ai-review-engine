import Papa from 'papaparse';
import type { Review } from '../types/review';

const SHEET_META = {
  sheetId: import.meta.env.VITE_GOOGLE_SHEET_ID ?? '1BL-09eLm61Zy3OLFxxqQVLf-I148dC30qbaKWa618wI',
  sheetName: 'NL Spotify review Scrapped data',
  sourceLabel: 'Google Play · Spotify · India',
} as const;

function reviewsCsvUrl(): string {
  const override = import.meta.env.VITE_REVIEWS_CSV_URL;
  if (override) return override;
  return '/api/reviews.csv';
}

function toNumber(value: string | undefined): number {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
}

function normalizeRow(row: Record<string, string>): Review {
  return {
    id: row.id?.trim() ?? '',
    userName: row.userName?.trim() ?? 'Anonymous',
    userImage: row.userImage?.trim() ?? '',
    date: row.date?.trim() ?? '',
    score: toNumber(row.score),
    scoreText: row.scoreText?.trim() ?? '',
    url: row.url?.trim() ?? '',
    title: row.title?.trim() ?? '',
    text: row.text?.trim() ?? '',
    replyDate: row.replyDate?.trim() ?? '',
    replyText: row.replyText?.trim() ?? '',
    version: row.version?.trim() ?? '',
    thumbsUp: toNumber(row.thumbsUp),
    criterias: row.criterias?.trim() ?? '',
  };
}

export async function fetchReviews(): Promise<Review[]> {
  const response = await fetch(reviewsCsvUrl());

  if (!response.ok) {
    throw new Error(`Failed to load reviews (${response.status})`);
  }

  const csv = await response.text();
  const parsed = Papa.parse<Record<string, string>>(csv, {
    header: true,
    skipEmptyLines: true,
  });

  if (parsed.errors.length > 0) {
    console.warn('CSV parse warnings:', parsed.errors);
  }

  return parsed.data
    .map(normalizeRow)
    .filter((review) => review.id || review.text || review.userName);
}

export function getSheetMeta() {
  return SHEET_META;
}
