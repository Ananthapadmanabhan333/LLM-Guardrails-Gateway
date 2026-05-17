"use client"

import { useEffect, useState } from "react"
import { Sidebar } from "../sidebar"
import { api, TimeSeriesPoint } from "@/lib/api"
import { formatNumber } from "@/lib/utils"
import {
  BarChart3, TrendingUp, Activity,
} from "lucide-react"
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts"

export default function AnalyticsPage() {
  const [requests, setRequests] = useState<TimeSeriesPoint[]>([])
  const [threats, setThreats] = useState<TimeSeriesPoint[]>([])

  useEffect(() => {
    Promise.all([api.getRequestsOverTime(24), api.getThreatsOverTime(24)]).then(([r, t]) => {
      setRequests(r.data)
      setThreats(t.data)
    })
  }, [])

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <main className="flex-1 ml-64 p-6 space-y-6">
        <div>
          <h1 className="text-2xl font-bold">Analytics</h1>
          <p className="text-sm text-muted-foreground mt-1">Usage trends and performance analytics</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="rounded-xl border border-border bg-card p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-sm font-semibold">Request Volume (24h)</h2>
              <Activity className="w-4 h-4 text-muted-foreground" />
            </div>
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={requests}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(217 33% 17%)" />
                  <XAxis dataKey="timestamp" tick={{ fontSize: 11, fill: "hsl(215 20% 65%)" }}
                    tickFormatter={(v) => new Date(v).toLocaleTimeString()} />
                  <YAxis tick={{ fontSize: 11, fill: "hsl(215 20% 65%)" }} />
                  <Tooltip contentStyle={{ background: "hsl(222 47% 14%)", border: "1px solid hsl(217 33% 17%)", borderRadius: "8px" }} />
                  <Line type="monotone" dataKey="count" stroke="#3b82f6" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="rounded-xl border border-border bg-card p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-sm font-semibold">Token Usage (24h)</h2>
              <BarChart3 className="w-4 h-4 text-muted-foreground" />
            </div>
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={requests}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(217 33% 17%)" />
                  <XAxis dataKey="timestamp" tick={{ fontSize: 11, fill: "hsl(215 20% 65%)" }}
                    tickFormatter={(v) => new Date(v).toLocaleTimeString()} />
                  <YAxis tick={{ fontSize: 11, fill: "hsl(215 20% 65%)" }} />
                  <Tooltip contentStyle={{ background: "hsl(222 47% 14%)", border: "1px solid hsl(217 33% 17%)", borderRadius: "8px" }} />
                  <Bar dataKey="tokens" fill="#10b981" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        <div className="rounded-xl border border-border bg-card p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold">Threat Trends (24h)</h2>
            <TrendingUp className="w-4 h-4 text-red-500" />
          </div>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={threats}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(217 33% 17%)" />
                <XAxis dataKey="timestamp" tick={{ fontSize: 11, fill: "hsl(215 20% 65%)" }}
                  tickFormatter={(v) => new Date(v).toLocaleTimeString()} />
                <YAxis tick={{ fontSize: 11, fill: "hsl(215 20% 65%)" }} />
                <Tooltip contentStyle={{ background: "hsl(222 47% 14%)", border: "1px solid hsl(217 33% 17%)", borderRadius: "8px" }} />
                <Line type="monotone" dataKey="count" stroke="#ef4444" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </main>
    </div>
  )
}
