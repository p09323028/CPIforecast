import { Link } from "react-router-dom";

export default function EmptyState({
  title,
  description,
  ctaLabel,
  ctaTo,
}: {
  title: string;
  description?: string;
  ctaLabel?: string;
  ctaTo?: string;
}) {
  return (
    <div className="rounded-lg border border-dashed border-slate-300 bg-white p-10 text-center">
      <h2 className="text-lg font-semibold text-slate-800">{title}</h2>
      {description && (
        <p className="mt-2 text-sm text-slate-500">{description}</p>
      )}
      {ctaLabel && ctaTo && (
        <Link
          to={ctaTo}
          className="inline-block mt-4 rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
        >
          {ctaLabel}
        </Link>
      )}
    </div>
  );
}
