"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { ClientSummary } from "@/types";

type SortKey = "name" | "sector" | "gap" | "opportunityScore" | "synShare";

const URGENCY_STYLES: Record<ClientSummary["urgency"], string> = {
  High: "bg-red-50 text-red-700 border-red-200",
  Medium: "bg-amber-50 text-amber-700 border-amber-200",
  Low: "bg-slate-50 text-slate-600 border-slate-200",
};

function formatZAR(value: number) {
  if (Math.abs(value) >= 1e9) return `R${(value / 1e9).toFixed(2)}B`;
  return `R${(value / 1e6).toFixed(0)}M`;
}

export default function ClientTable({ clients }: { clients: ClientSummary[] }) {
  const [sortKey, setSortKey] = useState<SortKey>("opportunityScore");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");

  const sorted = useMemo(() => {
    const copy = [...clients];
    copy.sort((a, b) => {
      const dir = sortDir === "asc" ? 1 : -1;
      const av = a[sortKey];
      const bv = b[sortKey];
      if (typeof av === "string" && typeof bv === "string")
        return av.localeCompare(bv) * dir;
      return ((av as number) - (bv as number)) * dir;
    });
    return copy;
  }, [clients, sortKey, sortDir]);

  function toggleSort(key: SortKey) {
    if (key === sortKey) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDir("desc");
    }
  }

  const headers: { key: SortKey; label: string }[] = [
    { key: "name", label: "Client" },
    { key: "sector", label: "Sector" },
    { key: "synShare", label: "Syn Share" },
    { key: "gap", label: "Wallet Gap" },
    { key: "opportunityScore", label: "Opportunity Score" },
  ];

  if (clients.length === 0) {
    return (
      <div className="rounded-[var(--radius-panel)] border border-dashed border-slate-300 bg-white p-8 text-center">
        <p className="text-sm font-medium text-slate-700">
          No client records available for this view.
        </p>
        <p className="mt-1 text-xs text-slate-500">
          Try adjusting filters or reload once backend data is available.
        </p>
      </div>
    );
  }

  return (
    <>
      {/* Mobile card list */}
      <div className="space-y-3 md:hidden">
        {sorted.map((c) => (
          <Link
            key={c.id}
            href={`/clients/${c.id}`}
            className="block rounded-[var(--radius-panel)] border border-slate-200/90 bg-white p-4 shadow-[var(--shadow-panel)] active:bg-slate-50"
          >
            <div className="flex items-start justify-between gap-2">
              <div className="min-w-0">
                <div className="truncate text-sm font-semibold text-slate-900">
                  {c.name}
                </div>
                <div className="text-xs text-slate-500">{c.sector}</div>
              </div>
              <span
                className={`shrink-0 rounded-full border px-2 py-0.5 text-xs font-medium ${URGENCY_STYLES[c.urgency]}`}
              >
                {c.urgency}
              </span>
            </div>
            <div className="mt-3 grid grid-cols-3 gap-2 text-center">
              <div>
                <div className="text-[10px] uppercase tracking-wide text-slate-500">
                  Syn Share
                </div>
                <div className="text-sm font-semibold text-[#0032A1]">
                  {(c.synShare * 100).toFixed(0)}%
                </div>
              </div>
              <div>
                <div className="text-[10px] uppercase tracking-wide text-slate-500">
                  Wallet Gap
                </div>
                <div className="text-sm font-semibold text-[#F2A900]">
                  {formatZAR(c.gap)}
                </div>
              </div>
              <div>
                <div className="text-[10px] uppercase tracking-wide text-slate-500">
                  Opp. Score
                </div>
                <div className="text-sm font-semibold text-[#0032A1]">
                  {c.opportunityScore}
                </div>
              </div>
            </div>
          </Link>
        ))}
      </div>

      {/* Desktop table */}
      <div className="hidden overflow-hidden rounded-[var(--radius-panel)] border border-slate-200/90 bg-white shadow-[var(--shadow-panel)] md:block">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-[var(--surface-muted)] text-left text-[11px] uppercase tracking-[0.1em] text-slate-600">
              <tr>
                {headers.map((h) => (
                  <th
                    key={h.key}
                    onClick={() => toggleSort(h.key)}
                    className="cursor-pointer select-none whitespace-nowrap px-4 py-3.5 font-semibold hover:text-[#0032A1]"
                  >
                    {h.label}{" "}
                    {sortKey === h.key && (sortDir === "asc" ? "↑" : "↓")}
                  </th>
                ))}
                <th className="px-4 py-3.5 font-semibold">Urgency</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {sorted.map((c) => (
                <tr key={c.id} className="transition-colors hover:bg-slate-50/90">
                  <td className="px-4 py-3.5 font-medium text-slate-900">
                    <Link
                      href={`/clients/${c.id}`}
                      className="hover:text-[#0032A1] hover:underline"
                    >
                      {c.name}
                    </Link>
                  </td>
                  <td className="px-4 py-3.5 text-slate-600">{c.sector}</td>
                  <td className="px-4 py-3.5 text-slate-700">
                    {(c.synShare * 100).toFixed(0)}%
                  </td>
                  <td className="px-4 py-3.5 font-semibold text-[#F2A900]">
                    {formatZAR(c.gap)}
                  </td>
                  <td className="px-4 py-3.5">
                    <div className="flex items-center gap-2">
                      <div className="h-1.5 w-20 rounded-full bg-slate-100">
                        <div
                          className="h-1.5 rounded-full bg-[#0032A1]"
                          style={{ width: `${c.opportunityScore}%` }}
                        />
                      </div>
                      <span className="text-xs font-medium text-slate-600">
                        {c.opportunityScore}
                      </span>
                    </div>
                  </td>
                  <td className="px-4 py-3.5">
                    <span
                      className={`rounded-full border px-2 py-0.5 text-xs font-medium ${URGENCY_STYLES[c.urgency]}`}
                    >
                      {c.urgency}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
