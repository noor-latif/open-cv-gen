export interface Profile {
  id: string
  clerk_user_id: string
  full_name: string | null
  email: string | null
  phone: string | null
  location: string | null
  linkedin_url: string | null
  portfolio_url: string | null
  professional_summary: string | null
  created_at: string
  updated_at: string
}

export interface WorkExperience {
  id: string
  profile_id: string
  company_name: string
  job_title: string
  start_date: string
  end_date: string | null
  is_current: boolean
  description: string | null
  achievements: string[] | null
  created_at: string
}

export interface Education {
  id: string
  profile_id: string
  institution: string
  degree: string
  field_of_study: string | null
  start_date: string | null
  end_date: string | null
  gpa: string | null
  achievements: string[] | null
  created_at: string
}

export interface Skill {
  id: string
  profile_id: string
  skill_name: string
  proficiency_level: "beginner" | "intermediate" | "advanced" | "expert" | null
  years_experience: number | null
  created_at: string
}

export interface JobApplication {
  id: string
  profile_id: string
  company_name: string
  job_title: string
  job_description: string | null
  job_url: string | null
  status: "saved" | "applied" | "interviewing" | "offer" | "rejected" | "withdrawn"
  match_score: "high" | "medium" | "low" | null
  match_assessment: string | null
  applied_at: string | null
  notes: string | null
  created_at: string
  updated_at: string
}

export interface GeneratedDocument {
  id: string
  job_application_id: string | null
  profile_id: string
  document_type: "cv" | "cover_letter"
  content: string
  tone: string | null
  language: string
  created_at: string
}

export interface ChatMessage {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: string
}

export interface ChatHistory {
  id: string
  profile_id: string
  messages: ChatMessage[]
  created_at: string
  updated_at: string
}

export interface UserProfile extends Profile {
  work_experience: WorkExperience[]
  education: Education[]
  skills: Skill[]
}
