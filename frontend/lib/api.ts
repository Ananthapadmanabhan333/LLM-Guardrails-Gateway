const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || "API Error")
  }
  return res.json()
}

export interface DashboardStats {
  total_requests: number
  blocked_requests: number
  total_threats: number
  block_rate: number
}

export interface MetricsSummary {
  total_requests: number
  total_tokens: number
  total_cost: number
  blocked_requests: number
  total_threats: number
  block_rate: number
  latency: {
    p50: number
    p95: number
    p99: number
    avg: number
  }
}

export interface ThreatEvent {
  id: string
  threat_type: string
  risk_level: string
  score: number
  detector_name: string
  matched_pattern?: string
  action_taken: string
  details: Record<string, unknown>
  created_at: string
}

export interface AuditLog {
  id: string
  event_type: string
  actor_id: string | null
  resource_type: string | null
  resource_id: string | null
  action: string | null
  details: Record<string, unknown>
  severity: string
  created_at: string
}

export interface RequestLog {
  id: string
  model: string
  provider: string
  tokens: number
  latency_ms: number
  cost_usd: number
  action: string
  risk_score: number
  is_blocked: boolean
  is_sanitized: boolean
  created_at: string
}

export interface ThreatStats {
  total_threats: number
  by_type: Record<string, number>
  by_severity: Record<string, number>
}

export interface TimeSeriesPoint {
  timestamp: string
  count: number
  tokens?: number
}

export interface LatencyPercentiles {
  p50: number
  p95: number
  p99: number
  avg: number
}

export const api = {
  getDashboard: () => fetchAPI<DashboardStats>("/audit/dashboard"),
  getMetricsSummary: () => fetchAPI<MetricsSummary>("/metrics/summary"),
  getLatency: (hours = 24) => fetchAPI<LatencyPercentiles>(`/metrics/latency?hours=${hours}`),
  getRequestsOverTime: (hours = 24) => fetchAPI<{ data: TimeSeriesPoint[] }>(`/metrics/requests?hours=${hours}`),
  getThreatsOverTime: (hours = 24) => fetchAPI<{ data: TimeSeriesPoint[] }>(`/metrics/threats?hours=${hours}`),
  getThreatStats: () => fetchAPI<ThreatStats>("/threats/stats"),
  getThreats: (page = 1, pageSize = 50) => fetchAPI<{ items: ThreatEvent[]; total: number }>(`/threats/?page=${page}&page_size=${pageSize}`),
  getAuditLogs: (page = 1, pageSize = 50) => fetchAPI<{ items: AuditLog[]; total: number }>(`/audit/logs?page=${page}&page_size=${pageSize}`),
  getRequestLogs: (page = 1, pageSize = 50) => fetchAPI<{ items: RequestLog[]; total: number }>(`/audit/requests?page=${page}&page_size=${pageSize}`),
  getPolicies: () => fetchAPI<{ policies: Record<string, unknown>; active_count: number; total_count: number }>("/policies/"),
  getProviders: () => fetchAPI<{ providers: Array<{ name: string; models: string[]; is_configured: boolean }> }>("/providers/"),
  analyzePrompt: (text: string) => fetchAPI<{ threat_score: number; risk_level: string; action: string }>(`/security/analyze/prompt?prompt=${encodeURIComponent(text)}`),
  health: () => fetchAPI<{ status: string; version: string }>("/health"),
}
