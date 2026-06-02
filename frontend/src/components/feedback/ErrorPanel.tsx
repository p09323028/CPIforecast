export default function ErrorPanel({
  title,
  detail,
  onRetry,
}: {
  title: string;
  detail?: string;
  onRetry?: () => void;
}) {
  return (
    <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-red-800">
      <p className="font-semibold">{title}</p>
      {detail && <p className="mt-1 text-sm">{detail}</p>}
      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="mt-3 rounded bg-red-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-red-700"
        >
          重試
        </button>
      )}
    </div>
  );
}
