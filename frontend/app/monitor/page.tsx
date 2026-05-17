"use client"

import { useEffect, useState } from "react"
import { Sidebar } from "../sidebar"
import { api, MetricsSummary, LatencyPercentiles } from "@/lib/api"
import { formatNumber, formatCurrency, formatLatency, formatPercent } from "@/lib/utils"
import {
  Activity, BarChart3, Clock, DollarSign, ShieldAlert, Zap,
} from "lucide-react"
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts"

export default function MonitorPage() {
  const [metrics, setMetrics] = useState<MetricsSummary | null>(null)
  const [latency, setLatency] = useState<LatencyPercentiles | null>(null)

  useEffect(() => {
    Promise.all([api.getMetricsSummary(), api.getLatency(24)]).then(([m, l]) => {
      setMetrics(m)
      setLatency(l)
    })
  }, [])

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <main className="flex-1 ml-64 p-6 space-y-6">
        <div>
          <h1 className="text-2xl font-bold">Real-time Monitor</h1>
          <p className="text-sm text-muted-foreground mt-1">Live system metrics and performance</p>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="rounded-xl border border-border bg-card p-4">
            <div className="flex items-center gap-2 text-muted-foreground mb-2">
              <Activity className="w-4 h-4" />
              <span className="text-xs">Requests</span>
            </div>
            <p className="text-xl font-bold">{formatNumber(metrics?.total_requests || 0)}</p>
          </div>
          <div className="rounded-xl border border-border bg-card p-4">
            <div className="flex items-center gap-2 text-muted-foreground mb-2">
              <Zap className="w-4 h-4" />
              <span className="text-xs">Tokens</span>
            </div>
            <p className="text-xl font-bold">{formatNumber(metrics?.total_tokens || 0)}</p>
          </div>
          <div className="rounded-xl border border-border bg-card p-4">
            <div className="flex items-center gap-2 text-muted-foreground mb-2">
              <DollarSign className="w-4 h-4" />
              <span className="text-xs">Cost</span>
            </div>
            <p className="text-xl font-bold">{formatCurrency(metrics?.total_cost || 0)}</p>
          </div>
          <div className="rounded-xl border border-border bg-card p-4">
            <div className="flex items-center gap-2 text-muted-foreground mb-2">
              <ShieldAlert className="w-4 h-4" />
              <span className="text-xs">Block Rate</span>
            </div>
            <p className="text-xl font-bold">{formatPercent(metrics?.block_rate || 0)}</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="rounded-xl border border-border bg-card p-6">
            <h2 className="text-sm font-semibold mb-4">Latency Distribution</h2>
            <div className="space-y-3">
              {latency && [
                { label: "P50", value: latency.p50, color: "bg-blue-500" },
                { label: "P95", value: latency.p95, color: "bg-orange-500" },
                { label: "P99", value: latency.p99, color: "bg-red-500" },
                { label: "Average", value: latency.avg, color: "bg-green-500" },
              ].map((item) => (
                <div key={item.label} className="space-y-1">
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">{item.label}</span>
                    <span className="font-medium">{formatLatency(item.value)}</span>
                  </div>
                  <div className="h-2 rounded-full bg-muted overflow-hidden">
                    <div
                      className={`h-full rounded-full ${item.color}`}
                      style={{ width: `${Math.min((item.value / (latency?.p99 || 1)) * 100, 100)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-xl border border-border bg-card p-6">
            <h2 className="text-sm font-semibold mb-4">System Health</h2>
            <div className="space-y-4">
              {[
                { label: "API Gateway", status: "operational", latency: "12ms" },
                { label: "Guardrails Engine", status: "operational", latency: "45ms" },
                { label: "Threat Detection", status: "operational", latency: "23ms" },
                { label: "LLM Router", status: "operational", latency: "156ms" },
                { label: "Database", status: "operational", latency: "3ms" },
                { label: "Redis Cache", status: "operational", latency: "1ms" },
              ].map((service) => (
                <div key={service.label} className="flex items-center justify-between py-2 border-b border-border last:border-0">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-green-500" />
                    <span className="text-sm">{service.label}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-xs text-green-500">{service.status}</span>
                    <span className="text-xs text-muted-foreground">{service.latency}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
