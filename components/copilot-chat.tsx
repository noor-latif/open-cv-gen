"use client"

import type React from "react"

import { useChat } from "@ai-sdk/react"
import { DefaultChatTransport } from "ai"
import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Card } from "@/components/ui/card"
import { Send, User, Bot, Loader2, FileText, Target, Mail } from "lucide-react"
import type { UserProfile } from "@/lib/types"
import { cn } from "@/lib/utils"

interface CopilotChatProps {
  profile: UserProfile | null
}

const QUICK_ACTIONS = [
  {
    icon: Target,
    label: "Analyze a job posting",
    prompt: "I'd like you to analyze a job posting for me. Here's the job description:\n\n[Paste job description here]",
  },
  {
    icon: FileText,
    label: "Generate a tailored CV",
    prompt:
      "Please help me create a tailored CV for a specific job position. Here's the job I'm applying for:\n\n[Paste job description here]",
  },
  {
    icon: Mail,
    label: "Write a cover letter",
    prompt: "I need help writing a cover letter. Here's the job posting:\n\n[Paste job description here]",
  },
]

export function CopilotChat({ profile }: CopilotChatProps) {
  const [input, setInput] = useState("")
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const { messages, sendMessage, status } = useChat({
    transport: new DefaultChatTransport({ api: "/api/chat" }),
    body: { profile },
  })

  const isLoading = status === "in_progress"

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    sendMessage({ text: input })
    setInput("")
  }

  const handleQuickAction = (prompt: string) => {
    setInput(prompt)
  }

  const hasProfile =
    profile?.full_name ||
    profile?.professional_summary ||
    (profile?.work_experience && profile.work_experience.length > 0) ||
    (profile?.skills && profile.skills.length > 0)

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center max-w-2xl mx-auto">
            <div className="w-12 h-12 bg-secondary rounded-full flex items-center justify-center mb-4">
              <Bot className="w-6 h-6" />
            </div>
            <h2 className="text-xl font-semibold mb-2">Job Application Copilot</h2>
            <p className="text-muted-foreground text-center mb-6 text-sm">
              {hasProfile
                ? "I can help you analyze job postings, generate tailored CVs, and write compelling cover letters based on your profile."
                : "Add your work experience and skills to your profile for personalized recommendations."}
            </p>

            {/* Quick Actions */}
            <div className="grid gap-3 w-full max-w-md">
              {QUICK_ACTIONS.map((action) => (
                <button
                  key={action.label}
                  onClick={() => handleQuickAction(action.prompt)}
                  className="flex items-center gap-3 p-4 border border-border rounded-lg hover:bg-secondary/50 transition-colors text-left"
                >
                  <action.icon className="w-5 h-5 text-muted-foreground" />
                  <span className="text-sm">{action.label}</span>
                </button>
              ))}
            </div>

            {!hasProfile && (
              <p className="text-xs text-muted-foreground mt-6">
                Tip: Complete your profile for more accurate job matching and document generation.
              </p>
            )}
          </div>
        ) : (
          <div className="max-w-3xl mx-auto space-y-6">
            {messages.map((message) => (
              <div
                key={message.id}
                className={cn("flex gap-4", message.role === "user" ? "justify-end" : "justify-start")}
              >
                {message.role === "assistant" && (
                  <div className="w-8 h-8 bg-secondary rounded-full flex items-center justify-center flex-shrink-0">
                    <Bot className="w-4 h-4" />
                  </div>
                )}
                <Card
                  className={cn(
                    "px-4 py-3 max-w-[80%]",
                    message.role === "user" ? "bg-foreground text-background" : "bg-secondary",
                  )}
                >
                  <div className="text-sm whitespace-pre-wrap">
                    {message.parts.map((part, index) => {
                      if (part.type === "text") {
                        return <span key={index}>{part.text}</span>
                      }
                      return null
                    })}
                  </div>
                </Card>
                {message.role === "user" && (
                  <div className="w-8 h-8 bg-foreground rounded-full flex items-center justify-center flex-shrink-0">
                    <User className="w-4 h-4 text-background" />
                  </div>
                )}
              </div>
            ))}
            {isLoading && (
              <div className="flex gap-4">
                <div className="w-8 h-8 bg-secondary rounded-full flex items-center justify-center flex-shrink-0">
                  <Bot className="w-4 h-4" />
                </div>
                <Card className="px-4 py-3 bg-secondary">
                  <Loader2 className="w-4 h-4 animate-spin" />
                </Card>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input */}
      <div className="border-t border-border p-4">
        <form onSubmit={handleSubmit} className="max-w-3xl mx-auto">
          <div className="flex gap-3">
            <Textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Paste a job description or ask for help..."
              className="min-h-[60px] max-h-[200px] resize-none"
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault()
                  handleSubmit(e)
                }
              }}
            />
            <Button type="submit" size="icon" className="h-[60px] w-[60px]" disabled={!input.trim() || isLoading}>
              {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
            </Button>
          </div>
          <p className="text-xs text-muted-foreground mt-2 text-center">
            Press Enter to send, Shift+Enter for new line
          </p>
        </form>
      </div>
    </div>
  )
}
