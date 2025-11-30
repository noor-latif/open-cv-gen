"use client"

import { useAuth } from "@clerk/nextjs"
import { useEffect, useState } from "react"
import { CopilotChat } from "@/components/copilot-chat"
import { createClient } from "@/lib/supabase/client"
import type { UserProfile } from "@/lib/types"
import { Loader2 } from "lucide-react"

export default function CopilotPage() {
  const { userId, isLoaded } = useAuth()
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadProfile() {
      if (!userId) return

      const supabase = createClient()

      const { data: profileData } = await supabase.from("profiles").select("*").eq("clerk_user_id", userId).single()

      if (!profileData) {
        setLoading(false)
        return
      }

      const [workExp, education, skills] = await Promise.all([
        supabase
          .from("work_experience")
          .select("*")
          .eq("profile_id", profileData.id)
          .order("start_date", { ascending: false }),
        supabase.from("education").select("*").eq("profile_id", profileData.id).order("end_date", { ascending: false }),
        supabase.from("skills").select("*").eq("profile_id", profileData.id),
      ])

      setProfile({
        ...profileData,
        work_experience: workExp.data || [],
        education: education.data || [],
        skills: skills.data || [],
      })
      setLoading(false)
    }

    if (isLoaded && userId) {
      loadProfile()
    }
  }, [userId, isLoaded])

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center">
        <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col">
      <div className="border-b border-border px-6 py-4">
        <h1 className="text-lg font-semibold">Copilot</h1>
        <p className="text-sm text-muted-foreground">
          Your AI assistant for job matching, CV tailoring, and cover letter generation.
        </p>
      </div>
      <CopilotChat profile={profile} />
    </div>
  )
}
