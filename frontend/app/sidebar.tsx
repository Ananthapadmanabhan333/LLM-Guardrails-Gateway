"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import {
  Shield,
  Activity,
  AlertTriangle,
  FileText,
  Settings,
  BarChart3,
  Route,
  Users,
  Database,
  LayoutDashboard,
  Search,
} from "lucide-react"

const menuItems = [
  { icon: LayoutDashboard, label: "Dashboard", href: "/" },
  { icon: Activity, label: "Monitor", href: "/monitor" },
  { icon: AlertTriangle, label: "Threats", href: "/threats" },
  { icon: Search, label: "Analysis", href: "/analysis" },
  { icon: FileText, label: "Audit Logs", href: "/audit" },
  { icon: Route, label: "Routing", href: "/routing" },
  { icon: BarChart3, label: "Analytics", href: "/analytics" },
  { icon: Settings, label: "Policies", href: "/policies" },
  { icon: Database, label: "Providers", href: "/providers" },
  { icon: Users, label: "Admin", href: "/admin" },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <div className="fixed left-0 top-0 z-40 h-screen w-64 border-r border-sidebar-border bg-sidebar">
      <div className="flex items-center gap-3 px-6 py-5 border-b border-sidebar-border">
        <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-primary">
          <Shield className="w-6 h-6 text-white" />
        </div>
        <div>
          <h1 className="text-sm font-semibold text-sidebar-foreground">Guardrails</h1>
          <p className="text-xs text-muted-foreground">AI Security Gateway</p>
        </div>
      </div>

      <nav className="p-3 space-y-1">
        {menuItems.map((item) => {
          const isActive = pathname === item.href
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all",
                isActive
                  ? "bg-primary/10 text-primary"
                  : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
              )}
            >
              <item.icon className={cn("w-4 h-4", isActive ? "text-primary" : "text-muted-foreground")} />
              {item.label}
            </Link>
          )
        })}
      </nav>

      <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-sidebar-border">
        <div className="flex items-center gap-3 px-3 py-2">
          <div className="w-2 h-2 rounded-full bg-green-500" />
          <span className="text-xs text-muted-foreground">All Systems Operational</span>
        </div>
      </div>
    </div>
  )
}
