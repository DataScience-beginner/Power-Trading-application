type SparklineChartProps = {
  values: number[];
  tone?: "accent" | "neutral" | "warning";
};

const TONE_BY_NAME = {
  accent: {
    fill: "rgba(14, 122, 105, 0.14)",
    stroke: "#0e7a69",
  },
  neutral: {
    fill: "rgba(54, 102, 179, 0.12)",
    stroke: "#3666b3",
  },
  warning: {
    fill: "rgba(211, 139, 33, 0.16)",
    stroke: "#d38b21",
  },
} as const;

// Inline SVG keeps the dashboard lightweight while still giving trend visibility.
export function SparklineChart({
  values,
  tone = "accent",
}: SparklineChartProps) {
  if (values.length < 2) {
    return <div className="sparkline-placeholder" />;
  }

  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;
  const points = values.map((value, index) => {
    const x = (index / (values.length - 1)) * 100;
    const y = 100 - ((value - min) / range) * 100;
    return `${x},${y}`;
  });
  const fillPoints = `0,100 ${points.join(" ")} 100,100`;
  const palette = TONE_BY_NAME[tone];

  return (
    <svg
      aria-hidden="true"
      className="sparkline-chart"
      preserveAspectRatio="none"
      viewBox="0 0 100 100"
    >
      <polygon fill={palette.fill} points={fillPoints} />
      <polyline
        fill="none"
        points={points.join(" ")}
        stroke={palette.stroke}
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="4"
      />
    </svg>
  );
}
