"use client"

import { Sidebar } from "../sidebar"
import { Users, Key, Shield, Settings } from "lucide-react"

export default function AdminPage() {
  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <main className="flex-1 ml-64 p-6 space-y-6">
        <div>
          <h1 className="text-2xl font-bold">Administration</h1>
          <p className="text-sm text-muted-foreground mt-1">Organization and system administration</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { title: "Organizations", desc: "Manage multi-tenant orgs", icon: Users, count: "3 Active" },
            { title: "API Keys", desc: "Manage access credentials", icon: Key, count: "12 Keys" },
            { title: "Security Settings", desc: "Configure security policies", icon: Shield, count: "8 Rules" },
            { title: "System Config", desc: "Platform configuration", icon: Settings, count: "v1.0.0" },
          ].map((item) => (
            <div key={item.title} className="rounded-xl border border-border bg-card p-5 card-hover">
              <div className="flex items-center gap-3 mb-3">
                <div className="p-2 rounded-lg bg-primary/10">
                  <item.icon className="w-4 h-4 text-primary" />
                </div>
                <span className="text-xs text-muted-foreground">{item.count}</span>
              </div>
              <h3 className="text-sm font-semibold">{item.title}</h3>
              <p className="text-xs text-muted-foreground mt-1">{item.desc}</p>
            </div>
          ))}
        </div>

        <div className="rounded-xl border border-border bg-card p-6">
          <h2 className="text-sm font-semibold mb-4">API Key Management</h2>
          <p className="text-sm text-muted-foreground">
            API key management is available through the admin API endpoint at <code className="px-1.5 py-0.5 rounded bg-muted text-xs font-mono">/admin/api-keys</code>.
          </p>
        </div>
      </main>
    </div>
  )
}
