import KpiCard from "@/components/KpiCard";
import ClientTable from "@/components/ClientTable";
import SectorBreakdownChart from "@/components/SectorBreakdownChart";
import { getPortfolio, getClients } from "@/lib/api";

function formatZAR(value: number) {
  if (Math.abs(value) >= 1e9) return `R${(value / 1e9).toFixed(1)}B`;
  return `R${(value / 1e6).toFixed(0)}M`;
}

export default async function PortfolioPage() {
  const [portfolio, clients] = await Promise.all([
    getPortfolio(),
    getClients(),
  ]);
  const topOpportunities = [...clients]
    .sort((a, b) => b.opportunityScore - a.opportunityScore)
    .slice(0, 5);

  return (
    <div className="space-y-8">
      <div className="space-y-3">
        <h1 className="text-2xl font-semibold tracking-tight text-slate-900 sm:text-3xl">
          Portfolio Overview
        </h1>
        <p className="text-sm text-slate-600">
          Across {portfolio.clientCount} JSE-listed corporate clients
        </p>
        <div className="h-0.5 w-16 origin-left rotate-[-27deg] bg-[#0032A1]/40" />
      </div>

      <div className="grid grid-cols-2 gap-3 sm:gap-4 md:grid-cols-4">
        <KpiCard
          label="Total Wallet"
          value={formatZAR(portfolio.totalWallet)}
        />
        <KpiCard
          label="Syn Bank Share"
          value={`${(portfolio.synShare * 100).toFixed(0)}%`}
        />
        <KpiCard
          label="Total Opportunity Gap"
          value={formatZAR(portfolio.totalGap)}
          accent
        />
        <KpiCard
          label="Clients Tracked"
          value={String(portfolio.clientCount)}
        />
      </div>

      <div>
        <h2 className="mb-3 text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-500">
          Wallet by Sector
        </h2>
        <SectorBreakdownChart data={portfolio.bySector} />
      </div>

      <div>
        <h2 className="mb-3 text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-500">
          Top Opportunities
        </h2>
        <ClientTable clients={topOpportunities} />
      </div>
    </div>
  );
}
