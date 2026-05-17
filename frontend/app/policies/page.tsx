"use client"

import { useEffect, useState } from "react"
import { Sidebar } from "../sidebar"
import { api } from "@/lib/api"
import { Shield, CheckCircle, XCircle } from "lucide-react"

export default function PoliciesPage() {
  const [policies, setPolicies] = useState<Record<string, any>>({})
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      try {
        const p = await api.getPolicies()
        setPolicies(p.policies)
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
          <h1 className="text-2xl font-bold">Policy Engine</h1>
          <p className="text-sm text-muted-foreground mt-1">Manage enterprise AI security policies</p>
        </div>

        <div className="grid gap-4">
          {loading ? (
            <div className="text-center py-12 text-muted-foreground">Loading policies...</div>
          ) : Object.keys(policies).length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
              <Shield className="w-12 h-12 mb-4" />
              <p>No policies configured</p>
            </div>
          ) : (
            Object.entries(policies).map(([name, policy]) => (
              <div key={name} className="rounded-xl border border-border bg-card p-5 card-hover">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3">
                    {policy.enabled ? (
                      <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                    ) : (
                      <XCircle className="w-5 h-5 text-muted-foreground mt-0.5" />
                    )}
                    <div>
                      <h3 className="text-sm font-semibold">{name.replace(/_/g, " ")}</h3>
                      <p className="text-xs text-muted-foreground mt-0.5">{policy.description || "No description"}</p>
                      {policy.config?.patterns && (
                        <div className="flex flex-wrap gap-1.5 mt-2">
                          {policy.config.patterns.map((p: string, i: number) => (
                            <span key={i} className="px-2 py-0.5 rounded bg-muted text-xs font-mono text-muted-foreground">
                              {p}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${policy.enabled ? "bg-green-500/10 text-green-500" : "bg-muted text-muted-foreground"}`}>
                    {policy.enabled ? "Active" : "Inactive"}
                  </span>
                </div>
              </div>
            ))
          )}
        </div>
      </main>
    </div>
  )
}
