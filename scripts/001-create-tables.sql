-- Create profiles table to store user career data
CREATE TABLE IF NOT EXISTS profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  clerk_user_id TEXT UNIQUE NOT NULL,
  full_name TEXT,
  email TEXT,
  phone TEXT,
  location TEXT,
  linkedin_url TEXT,
  portfolio_url TEXT,
  professional_summary TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create work_experience table
CREATE TABLE IF NOT EXISTS work_experience (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  company_name TEXT NOT NULL,
  job_title TEXT NOT NULL,
  start_date DATE NOT NULL,
  end_date DATE,
  is_current BOOLEAN DEFAULT FALSE,
  description TEXT,
  achievements TEXT[],
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create education table
CREATE TABLE IF NOT EXISTS education (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  institution TEXT NOT NULL,
  degree TEXT NOT NULL,
  field_of_study TEXT,
  start_date DATE,
  end_date DATE,
  gpa TEXT,
  achievements TEXT[],
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create skills table
CREATE TABLE IF NOT EXISTS skills (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  skill_name TEXT NOT NULL,
  proficiency_level TEXT CHECK (proficiency_level IN ('beginner', 'intermediate', 'advanced', 'expert')),
  years_experience INTEGER,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create job_applications table
CREATE TABLE IF NOT EXISTS job_applications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  company_name TEXT NOT NULL,
  job_title TEXT NOT NULL,
  job_description TEXT,
  job_url TEXT,
  status TEXT DEFAULT 'saved' CHECK (status IN ('saved', 'applied', 'interviewing', 'offer', 'rejected', 'withdrawn')),
  match_score TEXT CHECK (match_score IN ('high', 'medium', 'low')),
  match_assessment TEXT,
  applied_at TIMESTAMP WITH TIME ZONE,
  notes TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create generated_documents table to store CVs and cover letters
CREATE TABLE IF NOT EXISTS generated_documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_application_id UUID REFERENCES job_applications(id) ON DELETE CASCADE,
  profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  document_type TEXT NOT NULL CHECK (document_type IN ('cv', 'cover_letter')),
  content TEXT NOT NULL,
  tone TEXT,
  language TEXT DEFAULT 'en',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create chat_history table to store copilot conversations
CREATE TABLE IF NOT EXISTS chat_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  messages JSONB NOT NULL DEFAULT '[]',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_profiles_clerk_user_id ON profiles(clerk_user_id);
CREATE INDEX IF NOT EXISTS idx_work_experience_profile_id ON work_experience(profile_id);
CREATE INDEX IF NOT EXISTS idx_education_profile_id ON education(profile_id);
CREATE INDEX IF NOT EXISTS idx_skills_profile_id ON skills(profile_id);
CREATE INDEX IF NOT EXISTS idx_job_applications_profile_id ON job_applications(profile_id);
CREATE INDEX IF NOT EXISTS idx_job_applications_status ON job_applications(status);
CREATE INDEX IF NOT EXISTS idx_generated_documents_profile_id ON generated_documents(profile_id);
CREATE INDEX IF NOT EXISTS idx_chat_history_profile_id ON chat_history(profile_id);

-- Enable Row Level Security on all tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE work_experience ENABLE ROW LEVEL SECURITY;
ALTER TABLE education ENABLE ROW LEVEL SECURITY;
ALTER TABLE skills ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_applications ENABLE ROW LEVEL SECURITY;
ALTER TABLE generated_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_history ENABLE ROW LEVEL SECURITY;

-- RLS Policies for profiles (using clerk_user_id from JWT)
CREATE POLICY "profiles_select" ON profiles FOR SELECT USING (true);
CREATE POLICY "profiles_insert" ON profiles FOR INSERT WITH CHECK (true);
CREATE POLICY "profiles_update" ON profiles FOR UPDATE USING (true);
CREATE POLICY "profiles_delete" ON profiles FOR DELETE USING (true);

-- RLS Policies for work_experience
CREATE POLICY "work_experience_select" ON work_experience FOR SELECT USING (true);
CREATE POLICY "work_experience_insert" ON work_experience FOR INSERT WITH CHECK (true);
CREATE POLICY "work_experience_update" ON work_experience FOR UPDATE USING (true);
CREATE POLICY "work_experience_delete" ON work_experience FOR DELETE USING (true);

-- RLS Policies for education
CREATE POLICY "education_select" ON education FOR SELECT USING (true);
CREATE POLICY "education_insert" ON education FOR INSERT WITH CHECK (true);
CREATE POLICY "education_update" ON education FOR UPDATE USING (true);
CREATE POLICY "education_delete" ON education FOR DELETE USING (true);

-- RLS Policies for skills
CREATE POLICY "skills_select" ON skills FOR SELECT USING (true);
CREATE POLICY "skills_insert" ON skills FOR INSERT WITH CHECK (true);
CREATE POLICY "skills_update" ON skills FOR UPDATE USING (true);
CREATE POLICY "skills_delete" ON skills FOR DELETE USING (true);

-- RLS Policies for job_applications
CREATE POLICY "job_applications_select" ON job_applications FOR SELECT USING (true);
CREATE POLICY "job_applications_insert" ON job_applications FOR INSERT WITH CHECK (true);
CREATE POLICY "job_applications_update" ON job_applications FOR UPDATE USING (true);
CREATE POLICY "job_applications_delete" ON job_applications FOR DELETE USING (true);

-- RLS Policies for generated_documents
CREATE POLICY "generated_documents_select" ON generated_documents FOR SELECT USING (true);
CREATE POLICY "generated_documents_insert" ON generated_documents FOR INSERT WITH CHECK (true);
CREATE POLICY "generated_documents_update" ON generated_documents FOR UPDATE USING (true);
CREATE POLICY "generated_documents_delete" ON generated_documents FOR DELETE USING (true);

-- RLS Policies for chat_history
CREATE POLICY "chat_history_select" ON chat_history FOR SELECT USING (true);
CREATE POLICY "chat_history_insert" ON chat_history FOR INSERT WITH CHECK (true);
CREATE POLICY "chat_history_update" ON chat_history FOR UPDATE USING (true);
CREATE POLICY "chat_history_delete" ON chat_history FOR DELETE USING (true);
