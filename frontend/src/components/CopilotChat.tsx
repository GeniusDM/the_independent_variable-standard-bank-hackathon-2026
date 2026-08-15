"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { CopilotMessage } from "@/types";
import { askCopilot } from "@/lib/api";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const SUGGESTIONS = [
  "Which clients should I prioritize this week?",
  "Which clients are losing FX business to competitors?",
  "Why is Nkosi Infrastructure Partners ranked first?",
  "Generate a meeting briefing for Karoo Minerals.",
];

const STORAGE_KEY = "synbank-copilot-messages";

type ChatMessage = CopilotMessage & {
  id: string;
};

function createId() {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

export default function CopilotChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [hydrated, setHydrated] = useState(false);
  const streamRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const scrollRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    if (raw) {
      try {
        const parsed = JSON.parse(raw) as ChatMessage[];
        setMessages(parsed);
      } catch {
        sessionStorage.removeItem(STORAGE_KEY);
      }
    }
    setHydrated(true);
  }, []);

  useEffect(() => {
    if (!hydrated) return;
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
  }, [hydrated, messages]);

  useEffect(() => {
    if (!scrollRef.current) return;
    scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [messages, loading]);

  useEffect(() => {
    return () => {
      if (streamRef.current) clearInterval(streamRef.current);
    };
  }, []);

  const canSend = useMemo(
    () => input.trim().length > 0 && !loading,
    [input, loading],
  );

  function resetConversation() {
    if (streamRef.current) {
      clearInterval(streamRef.current);
      streamRef.current = null;
    }
    setMessages([]);
    setLoading(false);
    setInput("");
    sessionStorage.removeItem(STORAGE_KEY);
  }

  function streamAssistantReply(
    messageId: string,
    fullText: string,
    done: () => void,
  ) {
    if (streamRef.current) clearInterval(streamRef.current);

    let cursor = 0;
    const charsPerTick = 7;

    streamRef.current = setInterval(() => {
      cursor = Math.min(fullText.length, cursor + charsPerTick);
      const partial = fullText.slice(0, cursor);

      setMessages((prev) =>
        prev.map((m) => (m.id === messageId ? { ...m, content: partial } : m)),
      );

      if (cursor >= fullText.length) {
        if (streamRef.current) clearInterval(streamRef.current);
        streamRef.current = null;
        done();
      }
    }, 22);
  }

  async function send(question: string) {
    if (!question.trim() || loading) return;

    const userMessage: ChatMessage = {
      id: createId(),
      role: "user",
      content: question,
    };
    const assistantMessage: ChatMessage = {
      id: createId(),
      role: "assistant",
      content: "",
    };

    setInput("");
    setMessages((prev) => [...prev, userMessage, assistantMessage]);
    setLoading(true);

    try {
      const reply = await askCopilot(question);
      const responseText =
        reply.content.trim() ||
        "No grounded answer could be generated for that request.";

      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantMessage.id
            ? { ...m, sources: reply.sources ?? [] }
            : m,
        ),
      );

      streamAssistantReply(assistantMessage.id, responseText, () => {
        setLoading(false);
      });
    } catch {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantMessage.id
            ? {
                ...m,
                content:
                  "I could not generate a response right now. Please try again.",
                sources: [],
              }
            : m,
        ),
      );
      setLoading(false);
    }
  }

  return (
    <div className="flex h-[calc(100dvh-10rem)] min-h-[480px] flex-col rounded-[var(--radius-panel)] border border-slate-200/90 bg-white shadow-[var(--shadow-panel)] lg:h-[calc(100vh-11rem)] lg:min-h-[620px]">
      <div className="flex items-center justify-between border-b border-slate-200/80 bg-[var(--surface-muted)] px-4 py-3">
        <div>
          <div className="text-sm font-semibold text-slate-900">
            SynBank Copilot
          </div>
          <div className="text-xs text-slate-600">
            Grounded on portfolio wallet and opportunity signals
          </div>
        </div>
        <button
          type="button"
          onClick={resetConversation}
          className="rounded-lg border border-[#0032A1]/20 bg-white px-3 py-1.5 text-xs font-medium text-[#0032A1] transition-colors hover:bg-[#0032A1]/5"
        >
          New conversation
        </button>
      </div>

      <div
        ref={scrollRef}
        className="flex-1 space-y-5 overflow-y-auto bg-white p-5"
      >
        {messages.length === 0 && (
          <div className="rounded-xl border border-slate-200/80 bg-slate-50 p-4">
            <div className="mb-3 text-sm font-medium text-slate-700">
              Start with a grounded prompt
            </div>
            <div className="flex flex-wrap gap-2.5">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  onClick={() => send(s)}
                  className="rounded-full border border-[#0032A1]/20 bg-[#0032A1]/5 px-3 py-1.5 text-xs font-medium text-[#0032A1] transition-colors hover:bg-[#0032A1]/10"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}
        {messages.map((m, i) => (
          <div
            key={m.id}
            className={`flex gap-3 ${m.role === "user" ? "justify-end" : "justify-start"}`}
          >
            {m.role === "assistant" && (
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[#0032A1] text-xs font-semibold text-white">
                AI
              </div>
            )}
            <div
              className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm ${m.role === "user" ? "bg-[#0032A1] text-white" : "border border-slate-200/90 bg-slate-50 text-slate-900"}`}
            >
              {m.role === "assistant" ? (
                <div className="prose prose-sm max-w-none prose-headings:mb-2 prose-headings:mt-4 prose-headings:text-slate-900 prose-p:my-2 prose-p:text-slate-800 prose-strong:text-slate-900 prose-ul:my-2 prose-li:my-0.5">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {m.content || " "}
                  </ReactMarkdown>
                </div>
              ) : (
                <p>{m.content}</p>
              )}

              {m.role === "assistant" && m.sources && m.sources.length > 0 && (
                <details className="mt-3 rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs text-slate-700">
                  <summary className="cursor-pointer font-medium text-[#0032A1]">
                    Based on {m.sources.length} supporting data points
                  </summary>
                  <ul className="mt-2 list-inside list-disc space-y-1">
                    {m.sources.map((source, idx) => (
                      <li key={`${m.id}-source-${idx}`}>{source}</li>
                    ))}
                  </ul>
                </details>
              )}
            </div>
            {m.role === "user" && (
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[#005199] text-xs font-semibold text-white">
                You
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex items-center gap-2 text-xs text-slate-500">
            <span className="inline-block h-2 w-2 animate-pulse rounded-full bg-[#0032A1]" />
            SynBank Copilot is generating a grounded response...
          </div>
        )}

        {!hydrated && (
          <div className="text-xs text-slate-400">Loading conversation...</div>
        )}
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          send(input);
        }}
        className="flex gap-2 border-t border-slate-200/90 bg-white p-3"
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about a client, sector, or opportunity…"
          className="flex-1 rounded-xl border border-slate-200 px-3 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#0032A1]/30"
        />
        <button
          type="submit"
          disabled={!canSend}
          className="rounded-xl bg-[#0032A1] px-4 py-2.5 text-sm font-medium text-white transition-colors hover:bg-[#002a87] disabled:cursor-not-allowed disabled:opacity-50"
        >
          Send
        </button>
      </form>
    </div>
  );
}
