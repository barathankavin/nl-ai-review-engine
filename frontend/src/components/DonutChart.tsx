import type { Theme } from '../types/api';

const SEGMENT_COLORS = [
  '#1ed760',
  '#3b82f6',
  '#fbbf24',
  '#f87171',
  '#a78bfa',
  '#22d3ee',
  '#fb923c',
  '#e879f9',
  '#94a3b8',
  '#4ade80',
];

interface DonutChartProps {
  themes: Theme[];
}

export function DonutChart({ themes }: DonutChartProps) {
  if (themes.length === 0) return null;

  const total = themes.reduce((sum, theme) => sum + theme.review_count, 0) || 1;
  const radius = 54;
  const stroke = 22;
  const circumference = 2 * Math.PI * radius;
  let offset = 0;

  const segments = themes.map((theme, index) => {
    const fraction = theme.review_count / total;
    const length = fraction * circumference;
    const segment = {
      theme,
      color: SEGMENT_COLORS[index % SEGMENT_COLORS.length],
      dasharray: `${length} ${circumference - length}`,
      dashoffset: -offset,
      fraction,
    };
    offset += length;
    return segment;
  });

  return (
    <div className="donut-chart">
      <div className="donut-chart__visual">
        <svg viewBox="0 0 140 140" aria-hidden="true">
          <circle
            cx="70"
            cy="70"
            r={radius}
            fill="none"
            stroke="rgba(255,255,255,0.06)"
            strokeWidth={stroke}
          />
          {segments.map((segment) => (
            <circle
              key={segment.theme.id}
              cx="70"
              cy="70"
              r={radius}
              fill="none"
              stroke={segment.color}
              strokeWidth={stroke}
              strokeDasharray={segment.dasharray}
              strokeDashoffset={segment.dashoffset}
              transform="rotate(-90 70 70)"
              strokeLinecap="butt"
            />
          ))}
        </svg>
        <div className="donut-chart__center">
          <strong>{themes.length}</strong>
          <span>patterns</span>
        </div>
      </div>
      <ul className="donut-chart__legend">
        {segments.map((segment) => (
          <li key={segment.theme.id}>
            <span className="donut-chart__swatch" style={{ background: segment.color }} />
            <span className="donut-chart__legend-label">{segment.theme.label}</span>
            <span className="donut-chart__legend-value">
              {segment.theme.review_count} · {(segment.fraction * 100).toFixed(0)}%
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
