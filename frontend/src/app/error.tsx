"use client";

export default function GlobalError({ reset }: { reset: () => void }) {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center gap-4 text-center">
      <div className="text-4xl">⚠️</div>
      <h2 className="text-lg font-semibold text-slate-800">
        Could not reach the SynBank API
      </h2>
      <p className="max-w-sm text-sm text-slate-500">
        Make sure the FastAPI backend is running:
        <code className="ml-1 rounded bg-slate-100 px-1.5 py-0.5 text-xs text-slate-700">
          uvicorn backend.main:app --reload
        </code>
      </p>
      <button
        onClick={reset}
        className="rounded-xl bg-[#0032A1] px-4 py-2 text-sm font-medium text-white hover:bg-[#002a87]"
      >
        Retry
      </button>
    </div>
  );
}
