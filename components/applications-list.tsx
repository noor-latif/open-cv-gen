"use client"

import { useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { Building2, ExternalLink, MoreHorizontal, Calendar, Trash2, ChevronDown } from "lucide-react"
import type { JobApplication } from "@/lib/types"
import { createClient } from "@/lib/supabase/client"
import { useRouter } from "next/navigation"
import { cn } from "@/lib/utils"

interface ApplicationsListProps {
  applications: JobApplication[]
}

const STATUS_OPTIONS = [
  { value: "saved", label: "Saved", color: "bg-gray-100 text-gray-700" },
  { value: "applied", label: "Applied", color: "bg-blue-100 text-blue-700" },
  { value: "interviewing", label: "Interviewing", color: "bg-amber-100 text-amber-700" },
  { value: "offer", label: "Offer", color: "bg-green-100 text-green-700" },
  { value: "rejected", label: "Rejected", color: "bg-red-100 text-red-700" },
  { value: "withdrawn", label: "Withdrawn", color: "bg-gray-100 text-gray-500" },
] as const

const MATCH_SCORE_STYLES = {
  high: "bg-green-100 text-green-700",
  medium: "bg-amber-100 text-amber-700",
  low: "bg-red-100 text-red-700",
}

export function ApplicationsList({ applications }: ApplicationsListProps) {
  const [items, setItems] = useState(applications)
  const [filter, setFilter] = useState<string>("all")
  const router = useRouter()

  const filteredItems = filter === "all" ? items : items.filter((app) => app.status === filter)

  const handleStatusChange = async (id: string, newStatus: JobApplication["status"]) => {
    const supabase = createClient()

    const updates: Partial<JobApplication> = {
      status: newStatus,
      updated_at: new Date().toISOString(),
    }

    if (newStatus === "applied" && !items.find((a) => a.id === id)?.applied_at) {
      updates.applied_at = new Date().toISOString()
    }

    const { error } = await supabase.from("job_applications").update(updates).eq("id", id)

    if (!error) {
      setItems((prev) => prev.map((app) => (app.id === id ? { ...app, ...updates } : app)))
    }
  }

  const handleDelete = async (id: string) => {
    const supabase = createClient()

    const { error } = await supabase.from("job_applications").delete().eq("id", id)

    if (!error) {
      setItems((prev) => prev.filter((app) => app.id !== id))
    }
  }

  if (items.length === 0) {
    return (
      <Card>
        <CardContent className="py-12 text-center">
          <Building2 className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
          <h3 className="font-semibold mb-1">No applications yet</h3>
          <p className="text-sm text-muted-foreground">
            Add your first job application to start tracking your progress.
          </p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div>
      {/* Filters */}
      <div className="flex gap-2 mb-6 flex-wrap">
        <Button variant={filter === "all" ? "default" : "outline"} size="sm" onClick={() => setFilter("all")}>
          All ({items.length})
        </Button>
        {STATUS_OPTIONS.map((status) => {
          const count = items.filter((a) => a.status === status.value).length
          if (count === 0) return null
          return (
            <Button
              key={status.value}
              variant={filter === status.value ? "default" : "outline"}
              size="sm"
              onClick={() => setFilter(status.value)}
            >
              {status.label} ({count})
            </Button>
          )
        })}
      </div>

      {/* Applications List */}
      <div className="space-y-3">
        {filteredItems.map((application) => {
          const statusOption = STATUS_OPTIONS.find((s) => s.value === application.status)

          return (
            <Card key={application.id} className="hover:border-foreground/20 transition-colors">
              <CardContent className="py-4">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-semibold truncate">{application.job_title}</h3>
                      {application.match_score && (
                        <Badge
                          variant="secondary"
                          className={cn("text-xs", MATCH_SCORE_STYLES[application.match_score])}
                        >
                          {application.match_score.toUpperCase()} match
                        </Badge>
                      )}
                    </div>
                    <div className="flex items-center gap-2 text-sm text-muted-foreground mb-2">
                      <Building2 className="w-4 h-4" />
                      <span>{application.company_name}</span>
                      {application.job_url && (
                        <a
                          href={application.job_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="hover:text-foreground"
                        >
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      )}
                    </div>
                    {application.applied_at && (
                      <div className="flex items-center gap-1 text-xs text-muted-foreground">
                        <Calendar className="w-3 h-3" />
                        Applied {new Date(application.applied_at).toLocaleDateString()}
                      </div>
                    )}
                  </div>

                  <div className="flex items-center gap-2">
                    {/* Status Dropdown */}
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="outline" size="sm" className={cn("gap-1", statusOption?.color)}>
                          {statusOption?.label}
                          <ChevronDown className="w-3 h-3" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        {STATUS_OPTIONS.map((status) => (
                          <DropdownMenuItem
                            key={status.value}
                            onClick={() => handleStatusChange(application.id, status.value)}
                          >
                            <span className={cn("w-2 h-2 rounded-full mr-2", status.color.split(" ")[0])} />
                            {status.label}
                          </DropdownMenuItem>
                        ))}
                      </DropdownMenuContent>
                    </DropdownMenu>

                    {/* Actions Menu */}
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon" className="h-8 w-8">
                          <MoreHorizontal className="w-4 h-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={() => handleDelete(application.id)} className="text-destructive">
                          <Trash2 className="w-4 h-4 mr-2" />
                          Delete
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>
    </div>
  )
}
