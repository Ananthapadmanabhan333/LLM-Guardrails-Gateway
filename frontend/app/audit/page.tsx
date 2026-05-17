"use client"

import { useEffect, useState } from "react"
import { Sidebar } from "../sidebar"
import { api, AuditLog, RequestLog } from "@/lib/api"
import { getRiskColor, timeAgo } from "@/lib/utils"
import { FileText } from "lucide-react"

type Tab = "audit" | "requests"

export default function AuditPage() {
  const [tab, setTab] = useState<Tab>("audit")
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([])
  const [requestLogs, setRequestLogs] = useState<RequestLog[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      try {
        const [a, r] = await Promise.all([api.getAuditLogs(1, 100), api.getRequestLogs(1, 100)])
        setAuditLogs(a.items)
        setRequestLogs(r.items)
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
        <div>
          <h1 className="text-2xl font-bold">Audit Logs</h1>
          <p className="text-sm text-muted-foreground mt-1">Immutable audit trail and request history</p>
        </div>

        <div className="flex gap-2">
          <button
            onClick={() => setTab("audit")}
            className={`px-4 py-2 rounded-lg text-sm font-medium ${tab === "audit" ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"}`}
          >
            Audit Events
          </button>
          <button
            onClick={() => setTab("requests")}
            className={`px-4 py-2 rounded-lg text-sm font-medium ${tab === "requests" ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"}`}
          >
            Request Logs
          </button>
        </div>

        <div className="rounded-xl border border-border bg-card">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left p-4 text-xs text-muted-foreground font-medium">Event</th>
                  <th className="text-left p-4 text-xs text-muted-foreground font-medium">Severity</th>
                  <th className="text-left p-4 text-xs text-muted-foreground font-medium">Actor</th>
                  <th className="text-left p-4 text-xs text-muted-foreground font-medium">Resource</th>
                  <th className="text-left p-4 text-xs text-muted-foreground font-medium">Time</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr>
                    <td colSpan={5} className="p-8 text-center text-muted-foreground">Loading...</td>
                  </tr>
                ) : (
                  (tab === "audit" ? auditLogs : requestLogs).map((log) => (
                    <tr key={log.id} className="border-b border-border hover:bg-muted/50">
                      <td className="p-4">
                        <div className="flex items-center gap-2">
                          <FileText className="w-4 h-4 text-muted-foreground" />
                          <span className="text-sm capitalize">
                            {"event_type" in log ? (log as AuditLog).event_type.replace(/_/g, " ") : (log as RequestLog).action.replace(/_/g, " ")}
                          </span>
                        </div>
                      </td>
                      <td className="p-4">
                        <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium ${getRiskColor(log.severity || "low")}`}>
                          {log.severity || "low"}
                        </span>
                      </td>
                      <td className="p-4 text-sm text-muted-foreground">
                        {"actor_id" in log ? (log as AuditLog).actor_id || "system" : (log as RequestLog).model}
                      </td>
                      <td className="p-4 text-sm text-muted-foreground">
                        {"resource_type" in log ? (log as AuditLog).resource_type || "-" : (log as RequestLog).provider}
                      </td>
                      <td className="p-4 text-sm text-muted-foreground">{timeAgo(log.created_at)}</td>
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
