import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatNumber(num: number): string {
  if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`
  if (num >= 1000) return `${(num / 1000).toFixed(1)}K`
  return num.toLocaleString()
}

export function formatCurrency(amount: number): string {
  return `$${amount.toFixed(6)}`
}

export function formatLatency(ms: number): string {
  if (ms >= 1000) return `${(ms / 1000).toFixed(2)}s`
  return `${ms.toFixed(0)}ms`
}

export function formatPercent(pct: number): string {
  return `${pct.toFixed(1)}%`
}

export function getRiskColor(level: string): string {
  const colors: Record<string, string> = {
    critical: "text-red-500 bg-red-500/10 border-red-500/20",
    high: "text-orange-500 bg-orange-500/10 border-orange-500/20",
    medium: "text-yellow-500 bg-yellow-500/10 border-yellow-500/20",
    low: "text-blue-500 bg-blue-500/10 border-blue-500/20",
    safe: "text-green-500 bg-green-500/10 border-green-500/20",
  }
  return colors[level] || colors.safe
}

export function getActionColor(action: string): string {
  const colors: Record<string, string> = {
    allow: "text-green-500",
    sanitize: "text-yellow-500",
    block: "text-red-500",
    escalate: "text-orange-500",
    human_review: "text-purple-500",
  }
  return colors[action] || "text-gray-500"
}

export function getProviderColor(provider: string): string {
  const colors: Record<string, string> = {
    openai: "text-green-400",
    anthropic: "text-orange-400",
    gemini: "text-blue-400",
    groq: "text-purple-400",
    ollama: "text-yellow-400",
  }
  return colors[provider] || "text-gray-400"
}

export function timeAgo(date: string | Date): string {
  const now = new Date()
  const past = new Date(date)
  const diffMs = now.getTime() - past.getTime()
  const diffSecs = Math.floor(diffMs / 1000)
  const diffMins = Math.floor(diffSecs / 60)
  const diffHours = Math.floor(diffMins / 60)
  const diffDays = Math.floor(diffHours / 24)

  if (diffSecs < 60) return `${diffSecs}s ago`
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  return `${diffDays}d ago`
}
