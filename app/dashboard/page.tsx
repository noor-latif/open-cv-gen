"use client"

import { useAuth } from "@clerk/nextjs"
import { useEffect, useState } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { MessageSquare, Briefcase, FileText, Plus, Loader2 } from "lucide-react"
import { createClient } from "@/lib/supabase/client"
import type { Profile } from "@/lib/types"

interface Stats {
  totalApplications: number
  activeApplications: number
  documentsGenerated: number
}

export default function DashboardPage() {
  const { userId, isLoaded } = useAuth()
  const [profile, setProfile] = useState<Profile | null>(null)
  const [stats, setStats] = useState<Stats>({ totalApplications: 0, activeApplications: 0, documentsGenerated: 0 })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadData() {
      if (!userId) return

      const supabase = createClient()

      // Get or create profile
      let { data: existingProfile } = await supabase.from("profiles").select("*").eq("clerk_user_id", userId).single()

      if (!existingProfile) {
        const { data: newProfile } = await supabase.from("profiles").insert({ clerk_user_id: userId }).select().single()
        existingProfile = newProfile
      }

      setProfile(existingProfile)

      if (existingProfile) {
        // Get stats
        const [applicationsResult, documentsResult] = await Promise.all([
          supabase.from("job_applications").select("id, status").eq("profile_id", existingProfile.id),
          supabase.from("generated_documents").select("id").eq("profile_id", existingProfile.id),
        ])

        const applications = applicationsResult.data || []
        const documents = documentsResult.data || []

        setStats({
          totalApplications: applications.length,
          activeApplications: applications.filter((a) => ["applied", "interviewing"].includes(a.status)).length,
          documentsGenerated: documents.length,
        })
      }

      setLoading(false)
    }

    if (isLoaded && userId) {
      loadData()
    }
  }, [userId, isLoaded])

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center">
        <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
      </div>
    )
  }

  const isProfileComplete = profile?.full_name && profile?.professional_summary

  return (
    <div className="p-8 max-w-5xl">
      <div className="mb-8">
        <h1 className="text-2xl font-bold mb-2">Welcome back</h1>
        <p className="text-muted-foreground">
          {isProfileComplete
            ? "Ready to find your next opportunity?"
            : "Complete your profile to get personalized recommendations."}
        </p>
      </div>

      {/* Quick Actions */}
      <div className="grid md:grid-cols-3 gap-4 mb-8">
        <Link href="/dashboard/copilot">
          <Card className="hover:border-foreground/20 transition-colors cursor-pointer h-full">
            <CardHeader className="pb-2">
              <div className="w-10 h-10 bg-secondary rounded-md flex items-center justify-center mb-2">
                <MessageSquare className="w-5 h-5" />
              </div>
              <CardTitle className="text-base">Start Copilot</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>Chat with AI to analyze jobs, generate documents, or get career advice.</CardDescription>
            </CardContent>
          </Card>
        </Link>

        <Link href="/dashboard/applications">
          <Card className="hover:border-foreground/20 transition-colors cursor-pointer h-full">
            <CardHeader className="pb-2">
              <div className="w-10 h-10 bg-secondary rounded-md flex items-center justify-center mb-2">
                <Briefcase className="w-5 h-5" />
              </div>
              <CardTitle className="text-base">Track Applications</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>Manage your job applications and track their progress.</CardDescription>
            </CardContent>
          </Card>
        </Link>

        <Link href="/dashboard/profile">
          <Card className="hover:border-foreground/20 transition-colors cursor-pointer h-full">
            <CardHeader className="pb-2">
              <div className="w-10 h-10 bg-secondary rounded-md flex items-center justify-center mb-2">
                <FileText className="w-5 h-5" />
              </div>
              <CardTitle className="text-base">Update Profile</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>Keep your experience and skills up to date for better matches.</CardDescription>
            </CardContent>
          </Card>
        </Link>
      </div>

      {/* Stats */}
      <div className="grid md:grid-cols-3 gap-4 mb-8">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Total Applications</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{stats.totalApplications}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Active Applications</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{stats.activeApplications}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Documents Generated</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{stats.documentsGenerated}</p>
          </CardContent>
        </Card>
      </div>

      {/* CTA */}
      {!isProfileComplete && (
        <Card className="bg-secondary/50">
          <CardContent className="flex items-center justify-between py-6">
            <div>
              <h3 className="font-semibold mb-1">Complete your profile</h3>
              <p className="text-sm text-muted-foreground">
                Add your work experience and skills to get personalized job matches.
              </p>
            </div>
            <Link href="/dashboard/profile">
              <Button>
                <Plus className="w-4 h-4 mr-2" />
                Add Details
              </Button>
            </Link>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
