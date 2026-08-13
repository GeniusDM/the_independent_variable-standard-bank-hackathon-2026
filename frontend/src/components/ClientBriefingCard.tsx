import { Briefing } from "@/types";

export default function ClientBriefingCard({
  briefing,
}: {
  briefing: Briefing;
}) {
  return (
    <div className="rounded-[var(--radius-panel)] border border-slate-200/90 bg-white p-5 shadow-[var(--shadow-panel)]">
      <div className="mb-3 flex items-center gap-2">
        <div className="h-2 w-2 rounded-full bg-[#0032A1]" />
        <span className="text-[11px] font-semibold uppercase tracking-[0.12em] text-[#0032A1]">
          AI Briefing
        </span>
      </div>
      <p className="text-sm leading-relaxed text-slate-800">
        {briefing.summary}
      </p>

      {briefing.keySignals.length > 0 && (
        <div className="mt-4">
          <div className="text-[11px] font-semibold uppercase tracking-[0.1em] text-slate-500">
            Key Signals
          </div>
          <ul className="mt-2 list-inside list-disc space-y-1 text-sm text-slate-700">
            {briefing.keySignals.map((s, i) => (
              <li key={i}>{s}</li>
            ))}
          </ul>
        </div>
      )}

      {briefing.recommendedAgenda.length > 0 && (
        <div className="mt-4">
          <div className="text-[11px] font-semibold uppercase tracking-[0.1em] text-slate-500">
            Recommended Agenda
          </div>
          <ul className="mt-2 list-inside list-disc space-y-1 text-sm text-slate-700">
            {briefing.recommendedAgenda.map((a, i) => (
              <li key={i}>{a}</li>
            ))}
          </ul>
        </div>
      )}

      {briefing.risk && (
        <div className="mt-4 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-700">
          {briefing.risk}
        </div>
      )}
    </div>
  );
}
