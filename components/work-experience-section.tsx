"use client"

import type React from "react"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Checkbox } from "@/components/ui/checkbox"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Plus, Trash2, Loader2, Building2 } from "lucide-react"
import { createClient } from "@/lib/supabase/client"
import type { WorkExperience } from "@/lib/types"

interface WorkExperienceSectionProps {
  experiences: WorkExperience[]
  profileId: string
}

export function WorkExperienceSection({ experiences, profileId }: WorkExperienceSectionProps) {
  const [items, setItems] = useState(experiences)
  const [open, setOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const router = useRouter()

  const [formData, setFormData] = useState({
    company_name: "",
    job_title: "",
    start_date: "",
    end_date: "",
    is_current: false,
    description: "",
  })

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    const supabase = createClient()

    const { data, error } = await supabase
      .from("work_experience")
      .insert({
        profile_id: profileId,
        company_name: formData.company_name,
        job_title: formData.job_title,
        start_date: formData.start_date,
        end_date: formData.is_current ? null : formData.end_date || null,
        is_current: formData.is_current,
        description: formData.description || null,
      })
      .select()
      .single()

    setIsLoading(false)

    if (!error && data) {
      setItems((prev) => [data, ...prev])
      setFormData({
        company_name: "",
        job_title: "",
        start_date: "",
        end_date: "",
        is_current: false,
        description: "",
      })
      setOpen(false)
    }
  }

  const handleDelete = async (id: string) => {
    const supabase = createClient()
    const { error } = await supabase.from("work_experience").delete().eq("id", id)

    if (!error) {
      setItems((prev) => prev.filter((exp) => exp.id !== id))
    }
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle>Work Experience</CardTitle>
          <CardDescription>Your professional history</CardDescription>
        </div>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button size="sm">
              <Plus className="w-4 h-4 mr-2" />
              Add
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add Work Experience</DialogTitle>
              <DialogDescription>Add a position from your work history</DialogDescription>
            </DialogHeader>
            <form onSubmit={handleAdd}>
              <div className="grid gap-4 py-4">
                <div className="grid gap-2">
                  <Label htmlFor="company_name">Company Name *</Label>
                  <Input
                    id="company_name"
                    value={formData.company_name}
                    onChange={(e) => setFormData((prev) => ({ ...prev, company_name: e.target.value }))}
                    required
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="job_title">Job Title *</Label>
                  <Input
                    id="job_title"
                    value={formData.job_title}
                    onChange={(e) => setFormData((prev) => ({ ...prev, job_title: e.target.value }))}
                    required
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="grid gap-2">
                    <Label htmlFor="start_date">Start Date *</Label>
                    <Input
                      id="start_date"
                      type="date"
                      value={formData.start_date}
                      onChange={(e) => setFormData((prev) => ({ ...prev, start_date: e.target.value }))}
                      required
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="end_date">End Date</Label>
                    <Input
                      id="end_date"
                      type="date"
                      value={formData.end_date}
                      onChange={(e) => setFormData((prev) => ({ ...prev, end_date: e.target.value }))}
                      disabled={formData.is_current}
                    />
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="is_current"
                    checked={formData.is_current}
                    onCheckedChange={(checked) => setFormData((prev) => ({ ...prev, is_current: checked as boolean }))}
                  />
                  <Label htmlFor="is_current" className="text-sm font-normal">
                    I currently work here
                  </Label>
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="description">Description</Label>
                  <Textarea
                    id="description"
                    value={formData.description}
                    onChange={(e) => setFormData((prev) => ({ ...prev, description: e.target.value }))}
                    placeholder="Key responsibilities and achievements..."
                  />
                </div>
              </div>
              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit" disabled={isLoading}>
                  {isLoading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                  Add Experience
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </CardHeader>
      <CardContent>
        {items.length === 0 ? (
          <p className="text-sm text-muted-foreground text-center py-4">No work experience added yet</p>
        ) : (
          <div className="space-y-4">
            {items.map((exp) => (
              <div key={exp.id} className="flex items-start justify-between p-4 border border-border rounded-lg">
                <div className="flex gap-3">
                  <div className="w-10 h-10 bg-secondary rounded-md flex items-center justify-center flex-shrink-0">
                    <Building2 className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="font-medium">{exp.job_title}</h4>
                    <p className="text-sm text-muted-foreground">{exp.company_name}</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {new Date(exp.start_date).toLocaleDateString("en-US", { month: "short", year: "numeric" })}
                      {" - "}
                      {exp.is_current
                        ? "Present"
                        : exp.end_date
                          ? new Date(exp.end_date).toLocaleDateString("en-US", { month: "short", year: "numeric" })
                          : ""}
                    </p>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8 text-muted-foreground hover:text-destructive"
                  onClick={() => handleDelete(exp.id)}
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
