export function ChartSkeleton() {
  return (
    <div className="aspect-[16/9] min-h-[320px] w-full rounded-lg bg-slate-100 animate-pulse" />
  );
}

export function CardSkeleton() {
  return <div className="h-32 rounded-lg bg-slate-100 animate-pulse" />;
}

export function RowSkeleton() {
  return <div className="h-8 w-full rounded bg-slate-100 animate-pulse" />;
}
