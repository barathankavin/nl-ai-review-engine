interface RatingStarsProps {
  score: number;
  size?: 'sm' | 'md';
}

export function RatingStars({ score, size = 'md' }: RatingStarsProps) {
  const rounded = Math.round(score);

  return (
    <div className={`stars stars--${size}`} aria-label={`${score} out of 5 stars`}>
      {Array.from({ length: 5 }, (_, index) => (
        <span
          key={index}
          className={index < rounded ? 'stars__star stars__star--filled' : 'stars__star'}
        >
          ★
        </span>
      ))}
    </div>
  );
}
