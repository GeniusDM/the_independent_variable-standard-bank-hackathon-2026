import OpportunityHeatmap from "@/components/OpportunityHeatmap";
import ClientTable from "@/components/ClientTable";
import { getOpportunities } from "@/lib/api";

export default async function OpportunitiesPage() {
  const opportunities = await getOpportunities();

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-slate-900 sm:text-3xl">
          Opportunities
        </h1>
        <p className="text-sm text-slate-600">
          Ranked by composite opportunity score, not wallet gap alone
        </p>
      </div>

      <div>
        <h2 className="mb-3 text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-500">
          Heatmap
        </h2>
        <OpportunityHeatmap clients={opportunities} />
      </div>

      <div>
        <h2 className="mb-3 text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-500">
          Ranked List
        </h2>
        <ClientTable clients={opportunities} />
      </div>
    </div>
  );
}
