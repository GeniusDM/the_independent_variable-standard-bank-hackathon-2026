"use client";

import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";

interface SectorRow {
  sector: string;
  wallet: number;
  synVolume: number;
}

function formatZAR(value: number) {
  if (Math.abs(value) >= 1e12) return `R${(value / 1e12).toFixed(2)}T`;
  if (Math.abs(value) >= 1e9) return `R${(value / 1e9).toFixed(1)}B`;
  return `R${(value / 1e6).toFixed(0)}M`;
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function CustomTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  const syn = payload.find((p: { dataKey: string }) => p.dataKey === "Syn Bank Volume")?.value ?? 0;
  const gap = payload.find((p: { dataKey: string }) => p.dataKey === "Wallet Gap")?.value ?? 0;
  const total = syn + gap;
  const share = total > 0 ? ((syn / total) * 100).toFixed(1) : "0";
  return (
    <div className="rounded-lg border border-slate-200 bg-white px-3.5 py-3 shadow-lg text-xs">
      <div className="mb-2 font-semibold text-slate-800">{label}</div>
      <div className="space-y-1">
        <div className="flex items-center justify-between gap-6">
          <span className="flex items-center gap-1.5 text-slate-500">
            <span className="h-2 w-2 rounded-sm bg-[#0032A1]" />
            Syn Bank
          </span>
          <span className="font-medium text-slate-800">{formatZAR(syn)}</span>
        </div>
        <div className="flex items-center justify-between gap-6">
          <span className="flex items-center gap-1.5 text-slate-500">
            <span className="h-2 w-2 rounded-sm bg-[#F2A900]" />
            Gap
          </span>
          <span className="font-medium text-slate-800">{formatZAR(gap)}</span>
        </div>
        <div className="mt-1.5 border-t border-slate-100 pt-1.5 flex items-center justify-between gap-6">
          <span className="text-slate-400">Syn Share</span>
          <span className="font-semibold text-[#0032A1]">{share}%</span>
        </div>
      </div>
    </div>
  );
}

export default function SectorBreakdownChart({ data }: { data: SectorRow[] }) {
  if (data.length === 0) {
    return (
      <div className="rounded-[var(--radius-panel)] border border-dashed border-slate-300 bg-white p-8 text-center">
        <p className="text-sm font-medium text-slate-700">No sector-level wallet data available.</p>
        <p className="mt-1 text-xs text-slate-500">
          Portfolio sector breakdown will appear once data is loaded.
        </p>
      </div>
    );
  }

  const chartData = data.map((d) => ({
    sector: d.sector,
    "Syn Bank Volume": d.synVolume,
    "Wallet Gap": d.wallet - d.synVolume,
  }));

  return (
    <div className="rounded-[var(--radius-panel)] border border-slate-200/90 bg-white shadow-[var(--shadow-panel)]">
      {/* Custom legend */}
      <div className="flex items-center gap-5 border-b border-slate-100 px-5 py-3">
        {[
          { color: "#0032A1", label: "Syn Bank Volume" },
          { color: "#F2A900", label: "Wallet Gap" },
        ].map((l) => (
          <div key={l.label} className="flex items-center gap-1.5 text-[11px] text-slate-500">
            <span className="h-2.5 w-2.5 rounded-sm" style={{ backgroundColor: l.color }} />
            {l.label}
          </div>
        ))}
      </div>
      <div className="h-72 p-4">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} layout="vertical" margin={{ left: 8, right: 16 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" horizontal={false} />
            <XAxis type="number" tickFormatter={formatZAR} tick={{ fontSize: 11 }} axisLine={false} tickLine={false} />
            <YAxis type="category" dataKey="sector" width={130} tick={{ fontSize: 11 }} axisLine={false} tickLine={false} />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: "#f8fafc" }} />
            <Bar dataKey="Syn Bank Volume" stackId="a" fill="#0032A1" radius={[0, 0, 0, 0]} />
            <Bar dataKey="Wallet Gap" stackId="a" fill="#F2A900" radius={[0, 3, 3, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
