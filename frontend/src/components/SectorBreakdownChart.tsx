"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Legend,
} from "recharts";

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

export default function SectorBreakdownChart({ data }: { data: SectorRow[] }) {
  if (data.length === 0) {
    return (
      <div className="rounded-[var(--radius-panel)] border border-dashed border-slate-300 bg-white p-8 text-center">
        <p className="text-sm font-medium text-slate-700">
          No sector-level wallet data available.
        </p>
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
    <div className="h-80 rounded-[var(--radius-panel)] border border-slate-200/90 bg-white p-4 shadow-[var(--shadow-panel)]">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} layout="vertical" margin={{ left: 24 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
          <XAxis
            type="number"
            tickFormatter={formatZAR}
            tick={{ fontSize: 11 }}
          />
          <YAxis
            type="category"
            dataKey="sector"
            width={140}
            tick={{ fontSize: 11 }}
          />
          <Tooltip
            formatter={(value) => {
              const numericValue =
                typeof value === "number" ? value : Number(value ?? 0);
              return formatZAR(numericValue);
            }}
          />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          <Bar dataKey="Syn Bank Volume" stackId="a" fill="#0032A1" />
          <Bar dataKey="Wallet Gap" stackId="a" fill="#F2A900" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
