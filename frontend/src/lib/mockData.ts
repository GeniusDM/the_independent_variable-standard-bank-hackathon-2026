import { ClientSummary, PortfolioSummary, Briefing } from "@/types";

// Illustrative mock clients. Swap for real model output once
// models/wallet_engine.py and opportunity_engine.py are producing it —
// this file exists purely so the dashboard is demoable before the
// backend is finished, and as a shape reference for real API responses.
export const MOCK_CLIENTS: ClientSummary[] = [
  {
    id: "c001",
    name: "Karoo Minerals Ltd",
    sector: "Mining",
    synShare: 0.18,
    wallet: { low: 1550000000, base: 1800000000, high: 2050000000, confidence: 0.84 },
    synVolume: 324000000,
    gap: 1476000000,
    revenueOpportunity: 3690000,
    opportunityScore: 91,
    urgency: "High",
    topPillar: "Trade Finance",
    whySignal:
      "Rising import volumes and inventory build with no Syn Bank letters of credit issued in the last 2 quarters.",
    whatToPitch: "Import letter of credit facility sized to recent inventory growth.",
  },
  {
    id: "c002",
    name: "Highveld Retail Group",
    sector: "Retail",
    synShare: 0.32,
    wallet: { low: 780000000, base: 900000000, high: 1010000000, confidence: 0.79 },
    synVolume: 288000000,
    gap: 612000000,
    revenueOpportunity: 1530000,
    opportunityScore: 71,
    urgency: "Low",
    topPillar: "Transactional",
    whySignal: "Steady multi-provider transactional split, no recent change in banking behaviour.",
    whatToPitch: "Cash management consolidation proposal.",
  },
  {
    id: "c003",
    name: "Waterberg Manufacturing",
    sector: "Manufacturing",
    synShare: 0.11,
    wallet: { low: 1120000000, base: 1250000000, high: 1390000000, confidence: 0.81 },
    synVolume: 137500000,
    gap: 1112500000,
    revenueOpportunity: 2781250,
    opportunityScore: 87,
    urgency: "High",
    topPillar: "FX",
    whySignal: "72% foreign revenue exposure with Syn Bank processing only 15% of related FX payments.",
    whatToPitch: "FX hedging programme for USD-denominated export receivables.",
  },
  {
    id: "c004",
    name: "Sentinel Financial Services",
    sector: "Financial Services",
    synShare: 0.41,
    wallet: { low: 2050000000, base: 2300000000, high: 2540000000, confidence: 0.77 },
    synVolume: 943000000,
    gap: 1357000000,
    revenueOpportunity: 3392500,
    opportunityScore: 68,
    urgency: "Medium",
    topPillar: "Investment Banking",
    whySignal: "Debt schedule maturing within 6 months, no Syn Bank refinancing engagement yet.",
    whatToPitch: "Debt refinancing / capital markets advisory conversation.",
  },
  {
    id: "c005",
    name: "Cape Coastal Foods",
    sector: "Consumer Goods",
    synShare: 0.26,
    wallet: { low: 640000000, base: 720000000, high: 800000000, confidence: 0.83 },
    synVolume: 187000000,
    gap: 533000000,
    revenueOpportunity: 1332500,
    opportunityScore: 63,
    urgency: "Medium",
    topPillar: "Trade Finance",
    whySignal: "Growing export collections volume, tenor lengthening on recent shipments.",
    whatToPitch: "Export collection and working capital facility.",
  },
  {
    id: "c006",
    name: "Nkosi Infrastructure Partners",
    sector: "Infrastructure",
    synShare: 0.09,
    wallet: { low: 1780000000, base: 2020000000, high: 2260000000, confidence: 0.74 },
    synVolume: 182000000,
    gap: 1838000000,
    revenueOpportunity: 4595000,
    opportunityScore: 94,
    urgency: "High",
    topPillar: "Investment Banking",
    whySignal:
      "Large capex pipeline announced in a recent SENS filing with no visible Syn Bank project finance activity.",
    whatToPitch: "Project finance / syndicated lending pitch tied to the announced capex programme.",
  },
];

export function getMockPortfolio(): PortfolioSummary {
  const totalWallet = MOCK_CLIENTS.reduce((s, c) => s + c.wallet.base, 0);
  const totalSynVolume = MOCK_CLIENTS.reduce((s, c) => s + c.synVolume, 0);

  const bySectorMap: Record<string, { sector: string; wallet: number; synVolume: number }> = {};
  for (const c of MOCK_CLIENTS) {
    if (!bySectorMap[c.sector]) {
      bySectorMap[c.sector] = { sector: c.sector, wallet: 0, synVolume: 0 };
    }
    bySectorMap[c.sector].wallet += c.wallet.base;
    bySectorMap[c.sector].synVolume += c.synVolume;
  }

  return {
    totalWallet,
    synShare: totalSynVolume / totalWallet,
    totalGap: totalWallet - totalSynVolume,
    clientCount: MOCK_CLIENTS.length,
    bySector: Object.values(bySectorMap),
  };
}

export function getMockBriefing(clientId: string): Briefing {
  const client = MOCK_CLIENTS.find((c) => c.id === clientId);
  if (!client) {
    return { clientId, summary: "No briefing available for this client yet.", keySignals: [], recommendedAgenda: [], risk: null };
  }
  return {
    clientId,
    summary: `${client.name} shows an estimated wallet gap of R${(client.gap / 1e6).toFixed(0)}M, concentrated in ${client.topPillar}. ${client.whySignal}`,
    keySignals: [client.whySignal, `Current Syn Bank share: ${(client.synShare * 100).toFixed(0)}%`],
    recommendedAgenda: [
      client.whatToPitch,
      "Confirm current banking panel and relationship owner",
      "Align on pricing ahead of the pitch",
    ],
    risk: client.urgency === "High" ? "Time-sensitive — competitor activity is likely already underway." : null,
  };
}
