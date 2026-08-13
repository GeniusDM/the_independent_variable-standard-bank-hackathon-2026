"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, Users, TrendingUp, Bot, X } from "lucide-react";

const NAV_ITEMS = [
  { href: "/", label: "Portfolio", icon: LayoutDashboard },
  { href: "/clients", label: "Clients", icon: Users },
  { href: "/opportunities", label: "Opportunities", icon: TrendingUp },
  { href: "/copilot", label: "AI Copilot", icon: Bot },
];

interface SidebarProps {
  open?: boolean;
  onClose?: () => void;
}

export default function Sidebar({ open, onClose }: SidebarProps) {
  const pathname = usePathname();

  const inner = (
    <aside className="flex h-full w-64 shrink-0 flex-col bg-[#0032A1] text-white">
      <div className="border-b border-white/10 px-6 py-7">
        <div className="flex items-center justify-between">
          <div>
            <span className="text-xl font-semibold tracking-tight">SynBank</span>
            <div className="mt-1 text-xs font-medium uppercase tracking-[0.14em] text-white/60">
              Intelligence Platform
            </div>
          </div>
          {onClose && (
            <button
              onClick={onClose}
              className="rounded-lg p-1.5 text-white/60 hover:bg-white/10 hover:text-white lg:hidden"
              aria-label="Close menu"
            >
              <X size={18} />
            </button>
          )}
        </div>
        <div className="mt-4 h-0.5 w-12 origin-left rotate-[-27deg] bg-white/70" />
      </div>

      <nav className="flex-1 space-y-1 px-3 py-5">
        {NAV_ITEMS.map((item) => {
          const active = pathname === item.href;
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={onClose}
              className={`flex items-center gap-2.5 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors ${
                active
                  ? "bg-white text-[#0032A1] shadow-sm"
                  : "text-white/80 hover:bg-white/10 hover:text-white"
              }`}
            >
              <Icon size={16} />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="border-t border-white/10 px-6 py-5 space-y-1">
        <div className="text-[11px] leading-relaxed text-white/45">
          Syn Bank Share of Wallet Intelligence Engine
        </div>
        <div className="text-[10px] text-white/30">
          © {new Date().getFullYear()} Syn Bank. All rights reserved.
        </div>
      </div>
    </aside>
  );

  return (
    <>
      {/* Desktop: sticky sidebar */}
      <div className="hidden lg:flex lg:sticky lg:top-0 lg:h-screen lg:shrink-0">{inner}</div>

      {/* Mobile: drawer overlay */}
      {open !== undefined && (
        <>
          {/* Backdrop */}
          <div
            className={`fixed inset-0 z-40 bg-black/50 transition-opacity lg:hidden ${
              open ? "opacity-100" : "pointer-events-none opacity-0"
            }`}
            onClick={onClose}
          />
          {/* Drawer */}
          <div
            className={`fixed inset-y-0 left-0 z-50 min-h-screen transition-transform duration-300 lg:hidden ${
              open ? "translate-x-0" : "-translate-x-full"
            }`}
          >
            {inner}
          </div>
        </>
      )}
    </>
  );
}
