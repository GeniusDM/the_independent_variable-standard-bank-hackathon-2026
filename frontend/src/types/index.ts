export type Pillar = "Transactional" | "FX" | "Trade Finance" | "Investment Banking";

export interface WalletEstimate {
  low: number;
  base: number;
  high: number;
  confidence: number; // 0-1
}

export interface ClientSummary {
  id: string;
  name: string;
  sector: string;
  synShare: number; // 0-1
  wallet: WalletEstimate;
  synVolume: number;
  gap: number;
  /** Annual ZAR fee revenue the uncaptured gap represents. */
  revenueOpportunity: number;
  opportunityScore: number; // 0-100
  urgency: "Low" | "Medium" | "High";
  topPillar: Pillar;
  whySignal: string;
  whatToPitch: string;
}

export interface PortfolioSummary {
  totalWallet: number;
  synShare: number;
  totalGap: number;
  clientCount: number;
  bySector: { sector: string; wallet: number; synVolume: number }[];
}

export interface Briefing {
  clientId: string;
  summary: string;
  keySignals: string[];
  recommendedAgenda: string[];
  risk: string | null;
}

export interface CopilotMessage {
  role: "user" | "assistant";
  content: string;
  sources?: string[];
}
