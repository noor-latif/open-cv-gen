import { consumeStream, convertToModelMessages, streamText, type UIMessage } from "ai"
import type { UserProfile } from "@/lib/types"

export const maxDuration = 60

const SYSTEM_PROMPT = `You are a Job Application Copilot — an AI assistant that helps job seekers with:
1. Job matching assessment
2. Tailored CV generation
3. Personal letter (cover letter) generation

## Core Principles

### Anti-Hallucination Rules (CRITICAL)
- NEVER invent employers, job titles, degrees, certifications, or dates
- NEVER add skills, achievements, or experiences not provided by the user
- If the user's profile lacks information needed for a section, ask for it or note it as "To be provided"
- When unsure, ask clarifying questions rather than assume

### Job Match Assessment
When analyzing a job posting, provide:
- **Match Level**: HIGH / MEDIUM / LOW
- **Matching Strengths**: Skills and experiences that align
- **Gaps**: Required qualifications the user lacks
- **Recommendation**: Honest advice on whether to apply

### CV Generation Guidelines
- Create ATS-optimized, keyword-rich CVs
- Use reverse chronological format by default
- Include only verified information from the user's profile
- Optimize for the specific job requirements
- Format: Clean, professional, scannable

### Cover Letter Guidelines
- Tailor tone based on company culture (formal/conversational)
- Reference specific job requirements
- Highlight relevant achievements from the user's actual experience
- Keep concise (250-400 words unless specified)
- Never fabricate enthusiasm about experiences that don't exist

## Response Style
- Be direct and professional
- Use bullet points for clarity
- Provide actionable advice
- Ask clarifying questions when needed`

function buildUserContext(profile: UserProfile | null): string {
  if (!profile) {
    return "Note: The user has not provided their profile information yet. Ask them to complete their profile or provide relevant details."
  }

  const sections: string[] = []

  if (profile.full_name || profile.professional_summary) {
    sections.push(`## User Profile
Name: ${profile.full_name || "Not provided"}
Location: ${profile.location || "Not provided"}
Summary: ${profile.professional_summary || "Not provided"}`)
  }

  if (profile.work_experience && profile.work_experience.length > 0) {
    const expList = profile.work_experience
      .map(
        (exp) =>
          `- ${exp.job_title} at ${exp.company_name} (${exp.start_date} - ${exp.is_current ? "Present" : exp.end_date || "Not specified"})
  ${exp.description || ""}
  ${exp.achievements ? `Achievements: ${exp.achievements.join(", ")}` : ""}`,
      )
      .join("\n")
    sections.push(`## Work Experience\n${expList}`)
  }

  if (profile.education && profile.education.length > 0) {
    const eduList = profile.education
      .map((edu) => `- ${edu.degree}${edu.field_of_study ? ` in ${edu.field_of_study}` : ""} at ${edu.institution}`)
      .join("\n")
    sections.push(`## Education\n${eduList}`)
  }

  if (profile.skills && profile.skills.length > 0) {
    const skillList = profile.skills
      .map((s) => `${s.skill_name}${s.proficiency_level ? ` (${s.proficiency_level})` : ""}`)
      .join(", ")
    sections.push(`## Skills\n${skillList}`)
  }

  if (sections.length === 0) {
    return "Note: The user's profile is incomplete. Ask them to provide their work experience, education, and skills for better assistance."
  }

  return sections.join("\n\n")
}

export async function POST(req: Request) {
  const { messages, profile }: { messages: UIMessage[]; profile: UserProfile | null } = await req.json()

  const userContext = buildUserContext(profile)

  const systemMessage = `${SYSTEM_PROMPT}

---

## User's Career Profile

${userContext}`

  const prompt = convertToModelMessages(messages)

  const result = streamText({
    model: "anthropic/claude-sonnet-4-20250514",
    system: systemMessage,
    prompt,
    abortSignal: req.signal,
  })

  return result.toUIMessageStreamResponse({
    onFinish: async ({ isAborted }) => {
      if (isAborted) {
        console.log("Chat aborted")
      }
    },
    consumeSseStream: consumeStream,
  })
}
