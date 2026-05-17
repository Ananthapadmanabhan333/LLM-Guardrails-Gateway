"use client"

import { useEffect, useState } from "react"
import { Sidebar } from "../sidebar"
import { api } from "@/lib/api"
import { getProviderColor } from "@/lib/utils"
import { Server, CheckCircle, XCircle } from "lucide-react"

interface Provider {
  name: string
  models: string[]
  is_configured: boolean
  cost_rank: number
}

export default function ProvidersPage() {
  const [providers, setProviders] = useState<Provider[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getProviders().then((p) => {
      setProviders(p.providers)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <main className="flex-1 ml-64 p-6 space-y-6">
        <div>
          <h1 className="text-2xl font-bold">LLM Providers</h1>
          <p className="text-sm text-muted-foreground mt-1">Configured model providers and routing</p>
        </div>

        <div className="grid gap-4">
          {loading ? (
            <div className="text-center py-12 text-muted-foreground">Loading providers...</div>
          ) : (
            providers.map((provider) => (
              <div key={provider.name} className="rounded-xl border border-border bg-card p-5 card-hover">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <Server className={`w-5 h-5 ${getProviderColor(provider.name)}`} />
                    <div>
                      <h3 className="text-sm font-semibold capitalize">{provider.name}</h3>
                      <div className="flex flex-wrap gap-1.5 mt-2">
                        {provider.models.map((model) => (
                          <span key={model} className="px-2 py-0.5 rounded bg-muted text-xs font-mono text-muted-foreground">
                            {model}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${provider.is_configured ? "bg-green-500/10 text-green-500" : "bg-red-500/10 text-red-500"}`}>
                      {provider.is_configured ? "Configured" : "Missing Key"}
                    </span>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </main>
    </div>
  )
}
