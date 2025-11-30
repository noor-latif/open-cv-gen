"use client"

import { useAuth } from "@clerk/nextjs"
import { useEffect, useState } from "react"
import { ApplicationsList } from "@/components/applications-list"
import { AddApplicationDialog } from "@/components/add-application-dialog"
import { createClient } from "@/lib/supabase/client"
import type { JobApplication } from "@/lib/types"
import { Loader2 } from "lucide-react"

export default function ApplicationsPage() {
  const { userId, isLoaded } = useAuth()
  const [applications, setApplications] = useState<JobApplication[]>([])
  const [profileId, setProfileId] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadApplications() {
      if (!userId) return

      const supabase = createClient()

      const { data: profile } = await supabase.from("profiles").select("id").eq("clerk_user_id", userId).single()

      if (!profile) {
        setLoading(false)
        return
      }

      setProfileId(profile.id)

      const { data: apps } = await supabase
        .from("job_applications")
        .select("*")
        .eq("profile_id", profile.id)
        .order("created_at", { ascending: false })

      setApplications(apps || [])
      setLoading(false)
    }

    if (isLoaded && userId) {
      loadApplications()
    }
  }, [userId, isLoaded])

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center">
        <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
      </div>
    )
  }

  return (
    <div className="p-8 max-w-5xl">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold mb-1">Applications</h1>
          <p className="text-muted-foreground text-sm">Track and manage your job applications</p>
        </div>
        {profileId && <AddApplicationDialog profileId={profileId} />}
      </div>

      <ApplicationsList applications={applications} />
    </div>
  )
}
