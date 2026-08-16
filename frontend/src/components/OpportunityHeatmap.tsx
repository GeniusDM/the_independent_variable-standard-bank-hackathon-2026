import Link from "next/link";
import { ClientSummary, Pillar } from "@/types";

const PILLARS: Pillar[] = ["Transactional", "FX", "Trade Finance", "Investment Banking"];

// Deterministic per-client per-pillar score derived from the composite score
// so the heatmap is meaningful without extra API fields.
function pillarScore(client: ClientSummary, pillar: Pillar): number {
  const base = client.opportunityScore;
  const offsets: Record<Pillar, number> = {
    Transactional: client.topPillar === "Transactional" ? 18 : -12,
    FX: client.topPillar === "FX" ? 18 : -8,
    "Trade Finance": client.topPillar === "Trade Finance" ? 18 : -15,
    "Investment Banking": client.topPillar === "Investment Banking" ? 18 : -10,
  };
  return Math.min(100, Math.max(0, Math.round(base + offsets[pillar])));
}

// YlOrRd — yellow → orange → red (D3/Matplotlib standard sequential heatmap)
function cellColor(score: number): string {
  if (score >= 85) return "#800026";
  if (score >= 70) return "#bd0026";
  if (score >= 55) return "#e31a1c";
  if (score >= 40) return "#fc4e2a";
  if (score >= 28) return "#fd8d3c";
  if (score >= 16) return "#feb24c";
  if (score >= 6) return "#fed976";
  return "#ffffcc";
}

function textColor(score: number): string {
  return score >= 40 ? "#ffffff" : "#1e293b";
}

const URGENCY_DOT: Record<ClientSummary["urgency"], string> = {
  High: "bg-red-500",
  Medium: "bg-amber-400",
  Low: "bg-slate-300",
};

const URGENCY_LABEL: Record<ClientSummary["urgency"], string> = {
  High: "High",
  Medium: "Medium",
  Low: "Low",
};

const LEGEND = [
  { label: "0", color: "#ffffcc" },
  { label: "25", color: "#fed976" },
  { label: "50", color: "#fd8d3c" },
  { label: "75", color: "#e31a1c" },
  { label: "100", color: "#800026" },
];

export default function OpportunityHeatmap({ clients }: { clients: ClientSummary[] }) {
  const sorted = [...clients].sort((a, b) => b.opportunityScore - a.opportunityScore);

  if (sorted.length === 0) {
    return (
      <div className="rounded-[var(--radius-panel)] border border-dashed border-slate-300 bg-white p-8 text-center">
        <p className="text-sm font-medium text-slate-700">No opportunities available.</p>
        <p className="mt-1 text-xs text-slate-500">
          Opportunity scoring output will appear here once data loads.
        </p>
      </div>
    );
  }

  const header = (
    <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-100 px-4 py-3 sm:px-5">
      <span className="text-[11px] font-semibold uppercase tracking-[0.1em] text-slate-500">
        Opportunity Score by Client × Product Pillar
      </span>
      <div className="flex items-center gap-1.5">
        <span className="text-[10px] text-slate-400">Low</span>
        {LEGEND.map((l) => (
          <div
            key={l.label}
            className="h-3.5 w-5 rounded-sm sm:w-6"
            style={{ backgroundColor: l.color }}
            title={l.label}
          />
        ))}
        <span className="text-[10px] text-slate-400">High</span>
      </div>
    </div>
  );

  const footer = (
    <div className="flex flex-wrap gap-3 border-t border-slate-100 px-4 py-3 sm:gap-4 sm:px-5">
      {(["High", "Medium", "Low"] as const).map((u) => (
        <div key={u} className="flex items-center gap-1.5 text-[11px] text-slate-500">
          <span className={`h-2 w-2 rounded-full ${URGENCY_DOT[u]}`} />
          {URGENCY_LABEL[u]}
        </div>
      ))}
      <div className="ml-auto text-[11px] text-slate-400">
        Composite = weighted score across all pillars
      </div>
    </div>
  );

  return (
    <div className="rounded-[var(--radius-panel)] border border-slate-200/90 bg-white shadow-[var(--shadow-panel)]">
      {header}

      {/* ── Mobile: card list (< md) ── */}
      <div className="divide-y divide-slate-100 md:hidden">
        {sorted.map((c) => (
          <div key={c.id} className="px-4 py-3">
            {/* Client row */}
            <div className="mb-2 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className={`h-2 w-2 shrink-0 rounded-full ${URGENCY_DOT[c.urgency]}`} />
                <div>
                  <Link
                    href={`/clients/${c.id}`}
                    className="text-sm font-medium text-slate-800 hover:text-[#0032A1] hover:underline"
                  >
                    {c.name}
                  </Link>
                  <div className="text-[10px] text-slate-400">{c.sector}</div>
                </div>
              </div>
              {/* Composite badge */}
              <div
                className="flex h-8 w-12 shrink-0 items-center justify-center rounded text-xs font-bold ring-2 ring-inset ring-white/30"
                style={{
                  backgroundColor: cellColor(c.opportunityScore),
                  color: textColor(c.opportunityScore),
                }}
              >
                {c.opportunityScore.toFixed(0)}
              </div>
            </div>
            {/* Pillar grid 2×2 */}
            <div className="grid grid-cols-2 gap-1.5">
              {PILLARS.map((p) => {
                const score = pillarScore(c, p);
                return (
                  <div
                    key={p}
                    className="flex items-center justify-between rounded px-2 py-1.5"
                    style={{ backgroundColor: cellColor(score) }}
                  >
                    <span
                      className="truncate text-[10px] font-medium"
                      style={{ color: textColor(score) }}
                    >
                      {p}
                    </span>
                    <span
                      className="ml-1 shrink-0 text-xs font-bold"
                      style={{ color: textColor(score) }}
                    >
                      {score}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {/* ── Desktop: scrollable table (≥ md) ── */}
      <div className="hidden overflow-x-auto md:block">
        <table className="w-full border-collapse text-xs">
          <thead>
            <tr className="bg-slate-50">
              <th className="w-48 border-b border-slate-100 px-4 py-2.5 text-left text-[11px] font-semibold uppercase tracking-[0.1em] text-slate-500">
                Client
              </th>
              {PILLARS.map((p) => (
                <th
                  key={p}
                  className="whitespace-nowrap border-b border-slate-100 px-3 py-2.5 text-center text-[11px] font-semibold uppercase tracking-[0.1em] text-slate-500"
                >
                  {p}
                </th>
              ))}
              <th className="whitespace-nowrap border-b border-slate-100 px-3 py-2.5 text-center text-[11px] font-semibold uppercase tracking-[0.1em] text-slate-500">
                Composite
              </th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((c, i) => (
              <tr key={c.id} className={i % 2 === 0 ? "bg-white" : "bg-slate-50/50"}>
                <td className="border-b border-slate-100 px-4 py-2">
                  <div className="flex items-center gap-2">
                    <span
                      className={`h-1.5 w-1.5 shrink-0 rounded-full ${URGENCY_DOT[c.urgency]}`}
                    />
                    <Link
                      href={`/clients/${c.id}`}
                      className="max-w-[160px] truncate font-medium text-slate-800 hover:text-[#0032A1] hover:underline"
                    >
                      {c.name}
                    </Link>
                  </div>
                  <div className="ml-3.5 text-[10px] text-slate-400">{c.sector}</div>
                </td>
                {PILLARS.map((p) => {
                  const score = pillarScore(c, p);
                  return (
                    <td key={p} className="border-b border-slate-100 px-1 py-1 text-center">
                      <div
                        className="mx-auto flex h-9 w-full min-w-[52px] items-center justify-center rounded font-semibold transition-transform hover:scale-105"
                        style={{
                          backgroundColor: cellColor(score),
                          color: textColor(score),
                        }}
                        title={`${c.name} · ${p}: ${score}`}
                      >
                        {score}
                      </div>
                    </td>
                  );
                })}
                <td className="border-b border-slate-100 px-1 py-1 text-center">
                  <div
                    className="mx-auto flex h-9 w-full min-w-[52px] items-center justify-center rounded font-bold ring-2 ring-inset ring-white/30 transition-transform hover:scale-105"
                    style={{
                      backgroundColor: cellColor(c.opportunityScore),
                      color: textColor(c.opportunityScore),
                    }}
                    title={`Composite: ${c.opportunityScore.toFixed(0)}`}
                  >
                    {c.opportunityScore.toFixed(0)}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {footer}
    </div>
  );
}
