import { Cpu, LoaderCircle, TriangleAlert } from "lucide-react";
import type { HealthStatus } from "../types";

interface RuntimeBadgeProps { health: HealthStatus | null; loading: boolean; }

export function RuntimeBadge({ health, loading }: RuntimeBadgeProps) {
  const isReady = health?.status === "ready";
  const isError = !loading && (!health || health.status === "error");
  const Icon = loading ? LoaderCircle : isError ? TriangleAlert : Cpu;
  const label = loading ? "Durum kontrol ediliyor" : isError ? "Yerel servis çevrimdışı" : health?.runtime === "ready" ? "Foundry Local • Hazır" : isReady ? "Yerel AI • İndeks hazır" : "Kurulum gerekli";
  return (
    <div className={`inline-flex min-h-9 items-center gap-2 rounded-full border px-3 text-xs font-semibold ${isError ? "border-amber-200 bg-amber-50 text-amber-800" : "border-emerald-200 bg-emerald-50 text-emerald-800"}`} title={health?.message} aria-label={label}>
      <Icon className={`size-3.5 ${loading ? "animate-spin" : ""}`} aria-hidden="true" />
      <span className="hidden sm:inline">{label}</span>
      <span className={`size-1.5 rounded-full ${isError ? "bg-amber-500" : "bg-emerald-500"}`} aria-hidden="true" />
    </div>
  );
}
