import { ClientSummary, PortfolioSummary, Briefing, CopilotMessage } from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    cache: "no-store",
    next: { revalidate: 0 },
  });
  if (!res.ok) throw new Error(`${path} → ${res.status}`);
  return res.json() as Promise<T>;
}

export function getPortfolio(): Promise<PortfolioSummary> {
  return apiFetch("/portfolio");
}

export function getClients(): Promise<ClientSummary[]> {
  return apiFetch("/clients");
}

export function getClient(id: string): Promise<ClientSummary | undefined> {
  return apiFetch<ClientSummary>(`/client/${id}`).catch(() => undefined);
}

export function getOpportunities(): Promise<ClientSummary[]> {
  return apiFetch("/opportunities");
}

export function getBriefing(id: string): Promise<Briefing> {
  return apiFetch(`/briefing/${id}`);
}

export async function askCopilot(question: string): Promise<CopilotMessage> {
  try {
    return await apiFetch("/ask-ai", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
  } catch {
    return {
      role: "assistant",
      content:
        "The AI copilot backend is not connected yet. Start the FastAPI server and ensure `/ask-ai` is live.",
      sources: [],
    };
  }
}
