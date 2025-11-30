"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Badge } from "@/components/ui/badge"
import { Plus, X, Loader2 } from "lucide-react"
import { createClient } from "@/lib/supabase/client"
import type { Skill } from "@/lib/types"

interface SkillsSectionProps {
  skills: Skill[]
  profileId: string
}

const PROFICIENCY_LEVELS = [
  { value: "beginner", label: "Beginner" },
  { value: "intermediate", label: "Intermediate" },
  { value: "advanced", label: "Advanced" },
  { value: "expert", label: "Expert" },
]

export function SkillsSection({ skills, profileId }: SkillsSectionProps) {
  const [items, setItems] = useState(skills)
  const [open, setOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  const [formData, setFormData] = useState({
    skill_name: "",
    proficiency_level: "" as Skill["proficiency_level"] | "",
  })

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    const supabase = createClient()

    const { data, error } = await supabase
      .from("skills")
      .insert({
        profile_id: profileId,
        skill_name: formData.skill_name,
        proficiency_level: formData.proficiency_level || null,
      })
      .select()
      .single()

    setIsLoading(false)

    if (!error && data) {
      setItems((prev) => [...prev, data])
      setFormData({ skill_name: "", proficiency_level: "" })
      setOpen(false)
    }
  }

  const handleDelete = async (id: string) => {
    const supabase = createClient()
    const { error } = await supabase.from("skills").delete().eq("id", id)

    if (!error) {
      setItems((prev) => prev.filter((skill) => skill.id !== id))
    }
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle>Skills</CardTitle>
          <CardDescription>Technical and soft skills</CardDescription>
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
              <DialogTitle>Add Skill</DialogTitle>
              <DialogDescription>Add a skill to your profile</DialogDescription>
            </DialogHeader>
            <form onSubmit={handleAdd}>
              <div className="grid gap-4 py-4">
                <div className="grid gap-2">
                  <Label htmlFor="skill_name">Skill Name *</Label>
                  <Input
                    id="skill_name"
                    value={formData.skill_name}
                    onChange={(e) => setFormData((prev) => ({ ...prev, skill_name: e.target.value }))}
                    placeholder="e.g., JavaScript, Project Management"
                    required
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="proficiency_level">Proficiency Level</Label>
                  <Select
                    value={formData.proficiency_level}
                    onValueChange={(value) =>
                      setFormData((prev) => ({
                        ...prev,
                        proficiency_level: value as Skill["proficiency_level"],
                      }))
                    }
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select level" />
                    </SelectTrigger>
                    <SelectContent>
                      {PROFICIENCY_LEVELS.map((level) => (
                        <SelectItem key={level.value} value={level.value}>
                          {level.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit" disabled={isLoading}>
                  {isLoading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                  Add Skill
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </CardHeader>
      <CardContent>
        {items.length === 0 ? (
          <p className="text-sm text-muted-foreground text-center py-4">No skills added yet</p>
        ) : (
          <div className="flex flex-wrap gap-2">
            {items.map((skill) => (
              <Badge key={skill.id} variant="secondary" className="py-1 px-3 text-sm">
                {skill.skill_name}
                {skill.proficiency_level && (
                  <span className="ml-1 text-xs text-muted-foreground">({skill.proficiency_level})</span>
                )}
                <button onClick={() => handleDelete(skill.id)} className="ml-2 hover:text-destructive">
                  <X className="w-3 h-3" />
                </button>
              </Badge>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
