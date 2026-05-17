"use client"

import { useEffect, useState } from "react"
import { Sidebar } from "../sidebar"
import { api, ThreatEvent, ThreatStats } from "@/lib/api"
import { getRiskColor, timeAgo, getActionColor } from "@/lib/utils"
import { AlertTriangle, Shield, RefreshCw } from "lucide-react"

export default function ThreatsPage() {
  const [threats, setThreats] = useState<ThreatEvent[]>([])
  const [stats, setStats] = useState<ThreatStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      try {
        const [t, s] = await Promise.all([api.getThreats(1, 100), api.getThreatStats()])
        setThreats(t.items)
        setStats(s)
      } catch (e) {
        console.error(e)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <main className="flex-1 ml-64 p-6 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">Threat Detection</h1>
            <p className="text-sm text-muted-foreground mt-1">Real-time threat monitoring and analysis</p>
          </div>
          <button
            onClick={() => window.location.reload()}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary/10 text-primary text-sm hover:bg-primary/20"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
        </div>

        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="rounded-xl border border-border bg-card p-4">
              <p className="text-sm text-muted-foreground">Total Threats</p>
              <p className="text-2xl font-bold mt-1">{stats.total_threats}</p>
            </div>
            {Object.entries(stats.by_severity).map(([level, count]) => (
              <div key={level} className="rounded-xl border border-border bg-card p-4">
                <p className="text-sm text-muted-foreground capitalize">{level}</p>
                <p className={`text-2xl font-bold mt-1 ${getRiskColor(level).split(" ")[0]}`}>{count}</p>
              </div>
            ))}
          </div>
        )}

        <div className="rounded-xl border border-border bg-card">
          <div className="p-4 border-b border-border">
            <h2 className="text-sm font-semibold">Threat Events</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left p-4 text-xs text-muted-foreground font-medium">Type</th>
                  <th className="text-left p-4 text-xs text-muted-foreground font-medium">Risk Level</th>
                  <th className="text-left p-4 text-xs text-muted-foreground font-medium">Score</th>
                  <th className="text-left p-4 text-xs text-muted-foreground font-medium">Detector</th>
                  <th className="text-left p-4 text-xs text-muted-foreground font-medium">Action</th>
                  <th className="text-left p-4 text-xs text-muted-foreground font-medium">Time</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr>
                    <td colSpan={6} className="p-8 text-center text-muted-foreground">Loading threats...</td>
                  </tr>
                ) : threats.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="p-8 text-center text-muted-foreground">
                      <div className="flex flex-col items-center gap-2">
                        <Shield className="w-8 h-8" />
                        <p>No threats detected</p>
                      </div>
                    </td>
                  </tr>
                ) : (
                  threats.map((threat) => (
                    <tr key={threat.id} className="border-b border-border hover:bg-muted/50">
                      <td className="p-4">
                        <div className="flex items-center gap-2">
                          <AlertTriangle className="w-4 h-4 text-orange-500" />
                          <span className="text-sm capitalize">{threat.threat_type.replace(/_/g, " ")}</span>
                        </div>
                      </td>
                      <td className="p-4">
                        <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium ${getRiskColor(threat.risk_level)}`}>
                          {threat.risk_level}
                        </span>
                      </td>
                      <td className="p-4">
                        <span className="text-sm font-mono">{(threat.score * 100).toFixed(0)}%</span>
                      </td>
                      <td className="p-4 text-sm text-muted-foreground">{threat.detector_name}</td>
                      <td className="p-4">
                        <span className={`text-sm capitalize ${getActionColor(threat.action_taken)}`}>
                          {threat.action_taken.replace(/_/g, " ")}
                        </span>
                      </td>
                      <td className="p-4 text-sm text-muted-foreground">{timeAgo(threat.created_at)}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  )
}
