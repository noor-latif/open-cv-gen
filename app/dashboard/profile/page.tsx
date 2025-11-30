"use client"

import { useAuth } from "@clerk/nextjs"
import { useEffect, useState } from "react"
import { ProfileForm } from "@/components/profile-form"
import { WorkExperienceSection } from "@/components/work-experience-section"
import { SkillsSection } from "@/components/skills-section"
import { createClient } from "@/lib/supabase/client"
import type { UserProfile } from "@/lib/types"
import { Loader2 } from "lucide-react"

export default function ProfilePage() {
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
      <div className="p-8 flex items-center justify-center">
        <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
      </div>
    )
  }

  return (
    <div className="p-8 max-w-3xl">
      <div className="mb-8">
        <h1 className="text-2xl font-bold mb-1">Profile</h1>
        <p className="text-muted-foreground text-sm">Manage your career information for personalized job matching</p>
      </div>

      <div className="space-y-8">
        <ProfileForm profile={profile} clerkUserId={userId!} />

        {profile && (
          <>
            <WorkExperienceSection experiences={profile.work_experience} profileId={profile.id} />
            <SkillsSection skills={profile.skills} profileId={profile.id} />
          </>
        )}
      </div>
    </div>
  )
}
