"use client"

import type React from "react"
import { UserButton, useAuth, RedirectToSignIn } from "@clerk/nextjs"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { FileText, Briefcase, User, MessageSquare, Home } from "lucide-react"
import { cn } from "@/lib/utils"

const NAV_ITEMS = [
  { href: "/dashboard", icon: Home, label: "Overview" },
  { href: "/dashboard/copilot", icon: MessageSquare, label: "Copilot" },
  { href: "/dashboard/applications", icon: Briefcase, label: "Applications" },
  { href: "/dashboard/profile", icon: User, label: "Profile" },
]

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const { isLoaded, isSignedIn } = useAuth()
  const pathname = usePathname()

  if (!isLoaded) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="animate-pulse text-muted-foreground">Loading...</div>
      </div>
    )
  }

  if (!isSignedIn) {
    return <RedirectToSignIn />
  }

  return (
    <div className="min-h-screen bg-background flex">
      {/* Sidebar */}
      <aside className="w-64 border-r border-border flex flex-col">
        <div className="p-4 border-b border-border">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-foreground rounded-md flex items-center justify-center">
              <FileText className="w-4 h-4 text-background" />
            </div>
            <span className="font-semibold">JobCopilot</span>
          </Link>
        </div>

        <nav className="flex-1 p-4">
          <ul className="space-y-1">
            {NAV_ITEMS.map((item) => (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 px-3 py-2 text-sm rounded-md transition-colors",
                    pathname === item.href
                      ? "bg-secondary text-foreground"
                      : "hover:bg-secondary/50 text-muted-foreground",
                  )}
                >
                  <item.icon className="w-4 h-4" />
                  {item.label}
                </Link>
              </li>
            ))}
          </ul>
        </nav>

        <div className="p-4 border-t border-border">
          <div className="flex items-center gap-3">
            <UserButton afterSignOutUrl="/" />
            <span className="text-sm text-muted-foreground">Account</span>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">{children}</main>
    </div>
  )
}
