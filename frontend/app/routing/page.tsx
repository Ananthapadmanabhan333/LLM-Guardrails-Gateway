"use client"

import { Sidebar } from "../sidebar"
import { Route, ArrowRight } from "lucide-react"

const routingFlow = [
  { step: "Request Received", desc: "API Gateway interception" },
  { step: "Guardrails Check", desc: "Security & policy validation" },
  { step: "Model Selection", desc: "Cost/latency optimization" },
  { step: "Provider Routing", desc: "OpenAI / Anthropic / etc." },
  { step: "Output Validation", desc: "Response safety check" },
  { step: "Response Delivered", desc: "Audit & metrics logged" },
]

export default function RoutingPage() {
  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <main className="flex-1 ml-64 p-6 space-y-6">
        <div>
          <h1 className="text-2xl font-bold">LLM Routing</h1>
          <p className="text-sm text-muted-foreground mt-1">Request routing and provider optimization</p>
        </div>

        <div className="rounded-xl border border-border bg-card p-6">
          <h2 className="text-sm font-semibold mb-6">Routing Pipeline</h2>
          <div className="space-y-0">
            {routingFlow.map((item, i) => (
              <div key={item.step} className="flex items-start gap-4 pb-6 relative">
                {i < routingFlow.length - 1 && (
                  <div className="absolute left-3 top-8 bottom-0 w-px bg-border" />
                )}
                <div className="flex items-center justify-center w-6 h-6 rounded-full bg-primary/20 border border-primary/50 z-10">
                  <span className="text-xs font-bold text-primary">{i + 1}</span>
                </div>
                <div>
                  <p className="text-sm font-medium">{item.step}</p>
                  <p className="text-xs text-muted-foreground">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-xl border border-border bg-card p-6">
          <h2 className="text-sm font-semibold mb-4">Routing Strategies</h2>
          <div className="grid grid-cols-2 gap-4">
            {[
              { name: "Cost-Optimized", desc: "Select cheapest model meeting requirements" },
              { name: "Latency-Optimized", desc: "Route to fastest available provider" },
              { name: "Capability-Based", desc: "Use strongest model for complex tasks" },
              { name: "Fallback Chain", desc: "Try primary, then secondary providers" },
            ].map((strategy) => (
              <div key={strategy.name} className="p-4 rounded-lg bg-muted border border-border">
                <div className="flex items-center gap-2 mb-1">
                  <Route className="w-4 h-4 text-primary" />
                  <span className="text-sm font-medium">{strategy.name}</span>
                </div>
                <p className="text-xs text-muted-foreground">{strategy.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  )
}
