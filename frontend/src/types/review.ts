export interface Review {
  id: string;
  userName: string;
  userImage: string;
  date: string;
  score: number;
  scoreText: string;
  url: string;
  title: string;
  text: string;
  replyDate: string;
  replyText: string;
  version: string;
  thumbsUp: number;
  criterias: string;
}

export type SortOption = 'newest' | 'oldest' | 'rating-high' | 'rating-low' | 'helpful';

export interface ReviewFilters {
  query: string;
  minScore: number | null;
  maxScore: number | null;
  hasReply: 'all' | 'yes' | 'no';
  sort: SortOption;
}

export interface ReviewStats {
  total: number;
  averageScore: number;
  withReply: number;
  distribution: Record<number, number>;
}

export interface SheetMeta {
  sheetId: string;
  sheetName: string;
  sourceLabel: string;
}
