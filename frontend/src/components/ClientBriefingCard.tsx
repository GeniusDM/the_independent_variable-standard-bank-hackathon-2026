import { AlertTriangle } from "lucide-react";
import { Briefing } from "@/types";

export default function ClientBriefingCard({ briefing }: { briefing: Briefing }) {
  return (
    <div className="rounded-[var(--radius-panel)] border border-slate-200/90 bg-white shadow-[var(--shadow-panel)]">
      {/* Header */}
      <div className="flex items-center gap-2 border-b border-slate-100 px-5 py-3">
        <span className="h-1.5 w-1.5 rounded-full bg-[#0032A1]" />
        <span className="text-[11px] font-semibold uppercase tracking-[0.12em] text-[#0032A1]">
          AI Briefing
        </span>
      </div>

      <div className="space-y-5 p-5">
        <p className="text-sm leading-relaxed text-slate-700">{briefing.summary}</p>

        {briefing.keySignals.length > 0 && (
          <div>
            <div className="mb-2 text-[11px] font-semibold uppercase tracking-[0.1em] text-slate-400">
              Key Signals
            </div>
            <div className="flex flex-wrap gap-2">
              {briefing.keySignals.map((s, i) => (
                <span
                  key={i}
                  className="rounded bg-[#eef3fb] px-2.5 py-1 text-xs font-medium text-[#0032A1]"
                >
                  {s}
                </span>
              ))}
            </div>
          </div>
        )}

        {briefing.recommendedAgenda.length > 0 && (
          <div>
            <div className="mb-2 text-[11px] font-semibold uppercase tracking-[0.1em] text-slate-400">
              Meeting Agenda
            </div>
            <ol className="space-y-2">
              {briefing.recommendedAgenda.map((a, i) => (
                <li key={i} className="flex items-start gap-3 text-sm text-slate-700">
                  <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-[#0032A1]/8 text-[10px] font-bold text-[#0032A1]">
                    {i + 1}
                  </span>
                  {a}
                </li>
              ))}
            </ol>
          </div>
        )}

        {briefing.risk && (
          <div className="flex items-start gap-2.5 rounded-lg border border-amber-200 bg-amber-50 px-3.5 py-3">
            <AlertTriangle size={14} className="mt-0.5 shrink-0 text-amber-500" />
            <p className="text-xs leading-relaxed text-amber-800">{briefing.risk}</p>
          </div>
        )}
      </div>
    </div>
  );
}
