import type { Metadata } from "next";
import "./theme.css";
import "./globals.css";
import AppShell from "@/components/AppShell";

export const metadata: Metadata = {
  title: "SynBank Intelligence Platform",
  description:
    "Share of Wallet Intelligence Engine for Syn Bank coverage bankers",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-slate-50 text-slate-900 antialiased">
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
