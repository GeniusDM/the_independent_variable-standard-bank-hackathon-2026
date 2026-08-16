import CopilotChat from "@/components/CopilotChat";

export default function CopilotPage() {
  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <h1 className="text-2xl font-semibold tracking-tight text-slate-900 sm:text-3xl">
          AI Copilot
        </h1>
        <p className="text-sm text-slate-600">
          Grounded answers over the portfolio wallet and opportunity intelligence layer
        </p>
      </div>
      <CopilotChat />
    </div>
  );
}
