interface KpiCardProps {
  label: string;
  value: string;
  sublabel?: string;
  accent?: boolean;
}

export default function KpiCard({ label, value, sublabel, accent }: KpiCardProps) {
  return (
    <div className="relative overflow-hidden rounded-[var(--radius-panel)] border border-slate-200/90 bg-[var(--surface)] p-5 shadow-[var(--shadow-panel)]">
      <div
        className={`absolute -right-4 -top-4 h-16 w-16 rotate-[-27deg] ${
          accent ? "bg-[#F2A900]/10" : "bg-[#0032A1]/5"
        }`}
      />
      <div className="text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-500">
        {label}
      </div>
      <div
        className={`mt-2 text-2xl font-semibold leading-none sm:text-[1.85rem] ${accent ? "text-[#F2A900]" : "text-[#0032A1]"}`}
      >
        {value}
      </div>
      {sublabel && <div className="mt-2 text-xs text-slate-500">{sublabel}</div>}
    </div>
  );
}
