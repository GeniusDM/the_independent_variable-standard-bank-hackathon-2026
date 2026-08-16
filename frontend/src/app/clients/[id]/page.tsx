import Link from "next/link";
import { getClient, getBriefing } from "@/lib/api";
import ClientBriefingCard from "@/components/ClientBriefingCard";

function formatZAR(value: number) {
  if (Math.abs(value) >= 1e12) return `R${(value / 1e12).toFixed(2)}T`;
  if (Math.abs(value) >= 1e9) return `R${(value / 1e9).toFixed(2)}B`;
  return `R${(value / 1e6).toFixed(0)}M`;
}

// Next.js 15: dynamic route params are async — adjust if your project is on Next 14.
export default async function ClientDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const client = await getClient(id);
  const briefing = await getBriefing(id);

  if (!client) {
    return (
      <div>
        <Link
          href="/clients"
          className="text-sm text-[#0032A1] hover:underline"
        >
          ← Back to clients
        </Link>
        <p className="mt-4 text-sm text-slate-500">Client not found.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <Link href="/clients" className="text-sm text-[#0032A1] hover:underline">
        ← Back to clients
      </Link>

      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-slate-900 sm:text-3xl">
          {client.name}
        </h1>
        <p className="text-sm text-slate-600">{client.sector}</p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <div className="rounded-[var(--radius-panel)] border border-slate-200/90 bg-white p-4 shadow-[var(--shadow-panel)]">
          <div className="text-[11px] uppercase tracking-[0.1em] text-slate-500">
            Estimated Wallet
          </div>
          <div className="mt-1 text-xl font-semibold text-[#0032A1]">
            {formatZAR(client.wallet.base)}
          </div>
          <div className="text-xs text-slate-500">
            Range {formatZAR(client.wallet.low)} –{" "}
            {formatZAR(client.wallet.high)}
          </div>
          <div className="text-xs text-slate-500">
            Confidence {(client.wallet.confidence * 100).toFixed(0)}%
          </div>
        </div>
        <div className="rounded-[var(--radius-panel)] border border-slate-200/90 bg-white p-4 shadow-[var(--shadow-panel)]">
          <div className="text-[11px] uppercase tracking-[0.1em] text-slate-500">
            Syn Bank Share
          </div>
          <div className="mt-1 text-xl font-semibold text-[#0032A1]">
            {client.synShare * 100 < 10
              ? `${(client.synShare * 100).toFixed(1)}%`
              : `${(client.synShare * 100).toFixed(0)}%`}
          </div>
          <div className="text-xs text-slate-500">
            {formatZAR(client.synVolume)} captured
          </div>
        </div>
        <div className="rounded-[var(--radius-panel)] border border-slate-200/90 bg-white p-4 shadow-[var(--shadow-panel)]">
          <div className="text-[11px] uppercase tracking-[0.1em] text-slate-500">
            Revenue Oppty / yr
          </div>
          <div className="mt-1 text-xl font-semibold text-[#F2A900]">
            {formatZAR(client.revenueOpportunity)}
          </div>
          <div className="text-xs text-slate-500">
            on a {formatZAR(client.gap)} flow gap
          </div>
        </div>
        <div className="rounded-[var(--radius-panel)] border border-slate-200/90 bg-white p-4 shadow-[var(--shadow-panel)]">
          <div className="text-[11px] uppercase tracking-[0.1em] text-slate-500">
            Opportunity Score
          </div>
          <div className="mt-1 text-xl font-semibold text-[#0032A1]">
            {client.opportunityScore.toFixed(0)}
          </div>
        </div>
      </div>

      <div>
        <h2 className="mb-2 text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-500">
          Why This Client
        </h2>
        <p className="text-sm leading-relaxed text-slate-800">
          {client.whySignal}
        </p>
      </div>

      <div>
        <h2 className="mb-2 text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-500">
          What to Pitch
        </h2>
        <p className="text-sm leading-relaxed text-slate-800">
          {client.whatToPitch}
        </p>
      </div>

      <ClientBriefingCard briefing={briefing} />
    </div>
  );
}
