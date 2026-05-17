"use client"

import { useEffect, useState } from "react"
import { Sidebar } from "./sidebar"
import { api, DashboardStats, MetricsSummary, ThreatStats, TimeSeriesPoint } from "@/lib/api"
import { formatNumber, formatCurrency, formatLatency, formatPercent, getRiskColor } from "@/lib/utils"
import {
  Activity,
  AlertTriangle,
  BarChart3,
  DollarSign,
  Shield,
  ShieldAlert,
  Zap,
  ArrowUp,
  ArrowDown,
} from "lucide-react"
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts"

const COLORS = {
  critical: "#ef4444",
  high: "#f97316",
  medium: "#eab308",
  low: "#3b82f6",
  safe: "#22c55e",
}

function StatCard({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  color,
}: {
  title: string
  value: string
  subtitle?: string
  icon: React.ElementType
  trend?: { value: number; positive: boolean }
  color?: string
}) {
  return (
    <div className="relative overflow-hidden rounded-xl border border-border bg-card p-6 card-hover">
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <p className="text-sm text-muted-foreground">{title}</p>
          <p className={`text-2xl font-bold ${color || "text-foreground"}`}>{value}</p>
          {subtitle && <p className="text-xs text-muted-foreground">{subtitle}</p>}
        </div>
        <div className={`p-3 rounded-lg ${color ? `${color}/10` : "bg-primary/10"}`}>
          <Icon className={`w-5 h-5 ${color || "text-primary"}`} />
        </div>
      </div>
      {trend && (
        <div className={`flex items-center gap-1 mt-3 text-xs ${trend.positive ? "text-green-500" : "text-red-500"}`}>
          {trend.positive ? <ArrowUp className="w-3 h-3" /> : <ArrowDown className="w-3 h-3" />}
          <span>{trend.value}% from last hour</span>
        </div>
      )}
    </div>
  )
}

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [metrics, setMetrics] = useState<MetricsSummary | null>(null)
  const [threatStats, setThreatStats] = useState<ThreatStats | null>(null)
  const [requestsOverTime, setRequestsOverTime] = useState<TimeSeriesPoint[]>([])
  const [threatsOverTime, setThreatsOverTime] = useState<TimeSeriesPoint[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadData() {
      try {
        const [dash, met, ts, rot, tot] = await Promise.all([
          api.getDashboard(),
          api.getMetricsSummary(),
          api.getThreatStats(),
          api.getRequestsOverTime(6),
          api.getThreatsOverTime(6),
        ])
        setStats(dash)
        setMetrics(met)
        setThreatStats(ts)
        setRequestsOverTime(rot.data)
        setThreatsOverTime(tot.data)
      } catch (e) {
        console.error("Failed to load dashboard data", e)
      } finally {
        setLoading(false)
      }
    }
    loadData()
    const interval = setInterval(loadData, 30000)
    return () => clearInterval(interval)
  }, [])

  const threatPieData = threatStats
    ? Object.entries(threatStats.by_type).map(([name, value]) => ({ name, value }))
    : []

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <main className="flex-1 ml-64 p-6 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">Dashboard</h1>
            <p className="text-sm text-muted-foreground mt-1">AI Security Gateway Monitoring</p>
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-green-500/10 border border-green-500/20">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            <span className="text-xs text-green-500">Live</span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Total Requests"
            value={formatNumber(stats?.total_requests || 0)}
            subtitle="All time"
            icon={Activity}
            color="text-blue-500"
          />
          <StatCard
            title="Threats Blocked"
            value={formatNumber(stats?.blocked_requests || 0)}
            subtitle={`${formatPercent(stats?.block_rate || 0)} block rate`}
            icon={ShieldAlert}
            color="text-red-500"
          />
          <StatCard
            title="Total Threats"
            value={formatNumber(stats?.total_threats || 0)}
            subtitle="Detected across all vectors"
            icon={AlertTriangle}
            color="text-orange-500"
          />
          <StatCard
            title="Total Cost"
            value={formatCurrency(metrics?.total_cost || 0)}
            subtitle={`${formatNumber(metrics?.total_tokens || 0)} tokens used`}
            icon={DollarSign}
            color="text-green-500"
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="rounded-xl border border-border bg-card p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-sm font-semibold">Request Volume (6h)</h2>
              <BarChart3 className="w-4 h-4 text-muted-foreground" />
            </div>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={requestsOverTime}>
                  <defs>
                    <linearGradient id="requestGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(217 33% 17%)" />
                  <XAxis
                    dataKey="timestamp"
                    tick={{ fontSize: 11, fill: "hsl(215 20% 65%)" }}
                    tickFormatter={(v) => {
                      const d = new Date(v)
                      return `${d.getHours().toString().padStart(2, "0")}:${d.getMinutes().toString().padStart(2, "0")}`
                    }}
                  />
                  <YAxis tick={{ fontSize: 11, fill: "hsl(215 20% 65%)" }} />
                  <Tooltip
                    contentStyle={{
                      background: "hsl(222 47% 14%)",
                      border: "1px solid hsl(217 33% 17%)",
                      borderRadius: "8px",
                    }}
                    labelFormatter={(v) => new Date(v).toLocaleString()}
                  />
                  <Area
                    type="monotone"
                    dataKey="count"
                    stroke="#3b82f6"
                    fillOpacity={1}
                    fill="url(#requestGradient)"
                    strokeWidth={2}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="rounded-xl border border-border bg-card p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-sm font-semibold">Threat Activity (6h)</h2>
              <AlertTriangle className="w-4 h-4 text-orange-500" />
            </div>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={threatsOverTime}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(217 33% 17%)" />
                  <XAxis
                    dataKey="timestamp"
                    tick={{ fontSize: 11, fill: "hsl(215 20% 65%)" }}
                    tickFormatter={(v) => {
                      const d = new Date(v)
                      return `${d.getHours().toString().padStart(2, "0")}:${d.getMinutes().toString().padStart(2, "0")}`
                    }}
                  />
                  <YAxis tick={{ fontSize: 11, fill: "hsl(215 20% 65%)" }} />
                  <Tooltip
                    contentStyle={{
                      background: "hsl(222 47% 14%)",
                      border: "1px solid hsl(217 33% 17%)",
                      borderRadius: "8px",
                    }}
                    labelFormatter={(v) => new Date(v).toLocaleString()}
                  />
                  <Bar dataKey="count" fill="#ef4444" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="rounded-xl border border-border bg-card p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-sm font-semibold">Threats by Type</h2>
              <Shield className="w-4 h-4 text-muted-foreground" />
            </div>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={threatPieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={90}
                    paddingAngle={4}
                    dataKey="value"
                  >
                    {threatPieData.map((entry, index) => (
                      <Cell key={entry.name} fill={Object.values(COLORS)[index % Object.keys(COLORS).length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      background: "hsl(222 47% 14%)",
                      border: "1px solid hsl(217 33% 17%)",
                      borderRadius: "8px",
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="flex flex-wrap gap-3 mt-2">
              {threatPieData.map((entry, index) => (
                <div key={entry.name} className="flex items-center gap-1.5 text-xs text-muted-foreground">
                  <div
                    className="w-2.5 h-2.5 rounded-full"
                    style={{ backgroundColor: Object.values(COLORS)[index % Object.keys(COLORS).length] }}
                  />
                  <span className="capitalize">{entry.name.replace(/_/g, " ")}</span>
                  <span className="font-medium text-foreground">{entry.value}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-xl border border-border bg-card p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-sm font-semibold">Latency Metrics</h2>
              <Zap className="w-4 h-4 text-yellow-500" />
            </div>
            <div className="space-y-4">
              {[
                { label: "P50 Latency", value: formatLatency(metrics?.latency.p50 || 0) },
                { label: "P95 Latency", value: formatLatency(metrics?.latency.p95 || 0) },
                { label: "P99 Latency", value: formatLatency(metrics?.latency.p99 || 0) },
                { label: "Average Latency", value: formatLatency(metrics?.latency.avg || 0) },
              ].map((item) => (
                <div key={item.label} className="flex items-center justify-between py-2 border-b border-border last:border-0">
                  <span className="text-sm text-muted-foreground">{item.label}</span>
                  <span className="text-sm font-medium">{item.value}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-xl border border-border bg-card p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-sm font-semibold">Recent Threats</h2>
              <AlertTriangle className="w-4 h-4 text-red-500" />
            </div>
            <div className="space-y-3">
              {loading ? (
                <p className="text-sm text-muted-foreground">Loading...</p>
              ) : threatStats && threatStats.by_severity ? (
                <>
                  {threatStats.total_threats === 0 ? (
                    <div className="flex flex-col items-center justify-center py-8 text-muted-foreground">
                      <Shield className="w-8 h-8 mb-2" />
                      <p className="text-sm">No threats detected</p>
                    </div>
                  ) : (
                    Object.entries(threatStats.by_severity).map(([level, count]) => (
                      <div key={level} className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div className={`w-2 h-2 rounded-full ${getRiskColor(level)}`} />
                          <span className="text-sm capitalize">{level}</span>
                        </div>
                        <span className="text-sm font-medium">{count}</span>
                      </div>
                    ))
                  )}
                </>
              ) : null}
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
