import { SignInButton, SignUpButton, SignedIn, SignedOut } from "@clerk/nextjs"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import { FileText, Target, MessageSquare, ArrowRight } from "lucide-react"

export default function HomePage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-foreground rounded-md flex items-center justify-center">
              <FileText className="w-4 h-4 text-background" />
            </div>
            <span className="font-semibold text-lg">JobCopilot</span>
          </div>
          <div className="flex items-center gap-4">
            <SignedOut>
              <SignInButton mode="modal">
                <Button variant="ghost" size="sm">
                  Sign In
                </Button>
              </SignInButton>
              <SignUpButton mode="modal">
                <Button size="sm">Get Started</Button>
              </SignUpButton>
            </SignedOut>
            <SignedIn>
              <Link href="/dashboard">
                <Button size="sm">
                  Dashboard
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </Link>
            </SignedIn>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="max-w-6xl mx-auto px-6 py-24">
        <div className="text-center max-w-3xl mx-auto">
          <h1 className="text-5xl font-bold tracking-tight text-balance mb-6">
            Your AI-Powered Job Application Assistant
          </h1>
          <p className="text-xl text-muted-foreground mb-8 text-pretty">
            Get tailored CVs, compelling cover letters, and honest job match assessments. No hallucinations, no
            fabrications — just smart career support.
          </p>
          <SignedOut>
            <SignUpButton mode="modal">
              <Button size="lg" className="text-base px-8">
                Start Free
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            </SignUpButton>
          </SignedOut>
          <SignedIn>
            <Link href="/dashboard">
              <Button size="lg" className="text-base px-8">
                Go to Dashboard
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            </Link>
          </SignedIn>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-8 mt-24">
          <div className="p-6 border border-border rounded-lg">
            <div className="w-10 h-10 bg-secondary rounded-md flex items-center justify-center mb-4">
              <Target className="w-5 h-5 text-foreground" />
            </div>
            <h3 className="font-semibold text-lg mb-2">Job Match Analysis</h3>
            <p className="text-muted-foreground text-sm">
              Get honest High/Medium/Low match assessments with clear explanations of gaps and strengths.
            </p>
          </div>
          <div className="p-6 border border-border rounded-lg">
            <div className="w-10 h-10 bg-secondary rounded-md flex items-center justify-center mb-4">
              <FileText className="w-5 h-5 text-foreground" />
            </div>
            <h3 className="font-semibold text-lg mb-2">Tailored Documents</h3>
            <p className="text-muted-foreground text-sm">
              Generate ATS-optimized CVs and personalized cover letters based on your real experience.
            </p>
          </div>
          <div className="p-6 border border-border rounded-lg">
            <div className="w-10 h-10 bg-secondary rounded-md flex items-center justify-center mb-4">
              <MessageSquare className="w-5 h-5 text-foreground" />
            </div>
            <h3 className="font-semibold text-lg mb-2">AI Copilot Chat</h3>
            <p className="text-muted-foreground text-sm">
              Interactive assistant that helps you refine applications and prepare for opportunities.
            </p>
          </div>
        </div>
      </main>
    </div>
  )
}
