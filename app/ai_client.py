"""AI client using OpenAI SDK configured for Vercel AI Gateway."""

import json
import os
from typing import Dict, List, Optional

from openai import OpenAI


class AIClient:
    """AI client wrapper for Vercel AI Gateway or direct OpenAI API."""
    
    def __init__(self, config: Dict):
        """
        Initialize AI client.
        
        Args:
            config: Configuration dict with 'ai' key containing gateway_url, api_key, model
        """
        ai_config = config.get('ai', {})
        self.gateway_url = ai_config.get('gateway_url', '').strip() or os.getenv('VERCEL_AI_GATEWAY_URL', '').strip()
        api_key = ai_config.get('api_key', '').strip() or os.getenv('VERCEL_AI_API_KEY', '') or os.getenv('OPENAI_API_KEY', '')
        self.model = ai_config.get('model', 'gpt-4')
        
        if not api_key:
            raise ValueError("API key is required. Set VERCEL_AI_API_KEY or OPENAI_API_KEY environment variable, or configure in config.json")
        
        # Initialize OpenAI client
        # If gateway_url is provided, use it as base_url
        client_kwargs = {
            'api_key': api_key,
        }
        if self.gateway_url:
            # Ensure gateway URL ends with /v1 (OpenAI SDK expects this)
            gateway_url = self.gateway_url.rstrip('/')
            if not gateway_url.endswith('/v1'):
                if gateway_url.endswith('/v1'):
                    pass  # Already correct
                elif gateway_url.endswith('/v'):
                    gateway_url = gateway_url + '1'
                else:
                    gateway_url = gateway_url + '/v1'
            client_kwargs['base_url'] = gateway_url
            self.gateway_url = gateway_url
        
        self.client = OpenAI(**client_kwargs)
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.7) -> str:
        """
        Generate text using AI.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature (0-1)
        
        Returns:
            Generated text
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            error_msg = str(e)
            # Provide more helpful error messages
            if "404" in error_msg or "not found" in error_msg.lower():
                raise Exception(
                    f"AI API Gateway not found (404). Please check:\n"
                    f"1. Gateway URL is correct: {self.gateway_url or 'Using OpenAI directly'}\n"
                    f"2. Gateway exists and is accessible\n"
                    f"3. API key is valid\n"
                    f"Original error: {error_msg}"
                )
            raise Exception(f"AI API error: {error_msg}")
    
    def extract_skills(self, job_description: str) -> List[str]:
        """
        Extract required skills from job description.
        
        Returns:
            List of skill names
        """
        system_prompt = """You are a job description analyzer. Extract all technical skills, 
        tools, technologies, and competencies mentioned in the job description. 
        Return only a JSON array of skill names, nothing else."""
        
        prompt = f"""Extract all skills, technologies, and tools from this job description.
        Return only a JSON array of strings, no explanations.

Job Description:
{job_description}"""
        
        try:
            response = self.generate(prompt, system_prompt, temperature=0.3)
            # Try to parse JSON from response
            import json
            # Remove markdown code blocks if present
            response = response.strip()
            if response.startswith('```'):
                response = response.split('```')[1]
                if response.startswith('json'):
                    response = response[4:]
            response = response.strip()
            skills = json.loads(response)
            return skills if isinstance(skills, list) else []
        except Exception as e:
            # Fallback: return empty list
            return []
    
    def analyze_cv_job_alignment(self, cv_text: str, job_description: str) -> Dict:
        """
        Use semantic analysis to understand CV-job alignment.
        
        This method uses AI to semantically analyze how well a CV matches a job description,
        understanding context, synonyms, and related terms rather than simple keyword matching.
        
        Args:
            cv_text: Full text content of the CV
            job_description: Target job description
        
        Returns:
            Dict with:
                - required_skills: Key skills/requirements from job description
                - relevant_experience: Skills/experience from CV that match job (with evidence)
                - gaps: True gaps where CV genuinely lacks required experience
                - matched_experience: Experience in CV that matches job requirements
                - suggestions: How to highlight existing experience or address gaps
        """
        system_prompt = """You are an expert CV analyst. Analyze how well a CV matches a job description using semantic understanding, not keyword matching.

Consider:
- Synonyms and related terms (e.g., "IoT" = "Internet of Things" = "embedded systems")
- Context and experience level
- Transferable skills
- Experience mentioned in different sections (summary, work history, education, certifications)

Return ONLY valid JSON with this exact structure:
{
  "required_skills": ["list of key skills/requirements from job description"],
  "relevant_experience": ["list of skills/experience from CV that match job, with brief context"],
  "gaps": ["list of true gaps where CV genuinely lacks required experience"],
  "matched_experience": ["list of experience in CV that matches job requirements"],
  "suggestions": "text describing how to highlight existing experience or address gaps"
}

Do NOT include markdown code blocks. Return only the JSON object."""
        
        prompt = f"""Analyze this CV against the job description using semantic understanding.

Job Description:
{job_description}

CV Content:
{cv_text}

Identify:
1. What relevant experience/skills does the CV demonstrate for this job? (Consider synonyms, related terms, and context)
2. What are the actual gaps? (Only flag skills/experience that are truly missing, not just keyword mismatches)
3. How can the candidate highlight existing relevant experience?

Return valid JSON only with the structure specified in the system prompt."""
        
        try:
            response = self.generate(prompt, system_prompt, temperature=0.3)
            
            # Extract JSON from response
            response = response.strip()
            if '```json' in response:
                response = response.split('```json')[1].split('```')[0].strip()
            elif '```' in response:
                response = response.split('```')[1].split('```')[0].strip()
            
            analysis = json.loads(response)
            
            # Ensure all required keys exist
            return {
                'required_skills': analysis.get('required_skills', []),
                'relevant_experience': analysis.get('relevant_experience', []),
                'gaps': analysis.get('gaps', []),
                'matched_experience': analysis.get('matched_experience', []),
                'suggestions': analysis.get('suggestions', '')
            }
        except (json.JSONDecodeError, KeyError) as e:
            # Fallback to basic structure if parsing fails
            print(f"Warning: Failed to parse semantic analysis response: {e}")
            return {
                'required_skills': [],
                'relevant_experience': [],
                'gaps': [],
                'matched_experience': [],
                'suggestions': 'Unable to perform semantic analysis. Please check CV and job description.'
            }
    
    def analyze_skill_gaps(self, required_skills: List[str], cv_skills: List[str]) -> Dict:
        """
        Analyze gaps between required skills and CV skills.
        
        NOTE: This method is kept for backward compatibility. The new semantic analysis
        approach using analyze_cv_job_alignment() is preferred.
        
        Returns:
            Dict with 'missing', 'present', 'suggestions'
        """
        missing = [s for s in required_skills if s.lower() not in [cs.lower() for cs in cv_skills]]
        present = [s for s in required_skills if s.lower() in [cs.lower() for cs in cv_skills]]
        
        system_prompt = """You are a career advisor. Provide helpful suggestions for how someone 
        can acquire missing skills or demonstrate related experience."""
        
        if missing:
            prompt = f"""The following skills are required for a job but missing from the CV:
{', '.join(missing)}

The CV already has these related skills:
{', '.join(cv_skills[:10])}

Provide 2-3 brief suggestions for each missing skill on how to acquire it or demonstrate related experience. 
Format as a simple list."""
            
            suggestions = self.generate(prompt, system_prompt, temperature=0.7)
        else:
            suggestions = "All required skills are present in the CV!"
        
        return {
            'missing': missing,
            'present': present,
            'suggestions': suggestions
        }
    
    def tailor_cv(self, job_description: str, cv_html: str, historical_cvs: Optional[List[Dict]] = None) -> str:
        """
        Tailor CV content to match job description.
        
        Args:
            job_description: Target job description
            cv_html: Current CV HTML
            historical_cvs: Optional list of previous tailored CVs for context
        
        Returns:
            Tailored CV HTML
        """
        from app.cv_data import CVDataExtractor, CVRenderer
        
        # Extract CV data to JSON
        cv_data = CVDataExtractor.extract(cv_html)
        
        # Convert to JSON string for AI processing
        cv_json = json.dumps(cv_data, indent=2, ensure_ascii=False)
        
        # Build context from historical CVs
        historical_context = ""
        if historical_cvs:
            historical_context = "\n\nPrevious tailoring examples:\n"
            for hist in historical_cvs[:3]:
                historical_context += f"- {hist['company']} ({hist['job_title']}): Added skills {', '.join(hist.get('skills_added', []))}\n"
        
        # Extract current summary for style reference
        current_summary = cv_data.get('summary', '')
        
        system_prompt = """You are a CV tailoring expert. You will receive CV data in JSON format.
        Your task is to modify ONLY the text content to better match the job description while maintaining accuracy and authenticity.
        
        IMPORTANT RULES:
        1. Return ONLY valid JSON - no markdown code blocks, no explanations
        2. Preserve the exact JSON structure - all keys, arrays, and object structure must remain the same
        3. Only modify text values (strings) - do NOT change structure, add/remove keys, or modify arrays in ways that break the format
        4. You CAN add items to arrays (e.g., add a new project, add skills to a skill group)
        5. Professional Summary Tailoring:
           - MUST tailor the professional summary to emphasize relevant experience for this job
           - MAINTAIN the current writing style: concise, metrics-focused, uses strong action verbs
           - PRESERVE the structure: bold headings, specific numbers (e.g., "350+ engineers", "95%", "30%")
           - KEEP the authentic voice and tone - mimic the current style exactly
           - Use semantic understanding to highlight relevant experience, not just keyword matching
        6. Work experience bullets: highlight relevant achievements
        7. Skills section: ensure all relevant skills are visible (add missing ones to appropriate categories)
        
        Return the complete JSON object with tailored content."""
        
        prompt = f"""Tailor this CV data to match the job description below.

Job Description:
{job_description}

Current CV Data (JSON):
{cv_json}
{historical_context}

Current Professional Summary Style Reference:
{current_summary}

IMPORTANT: When tailoring the professional summary:
- Analyze the current summary style above and mimic it exactly
- Keep the same structure: bold headings, metrics, concise paragraphs
- Maintain the authentic voice and writing tone
- Use semantic understanding to emphasize relevant experience for this job
- Do NOT change the writing style - only adjust content to be more relevant

Return the tailored CV data as valid JSON. Only modify text content to better match the job.
You can add new skills to existing skill groups, add new projects, or enhance descriptions.
Do NOT change the JSON structure or remove existing data."""
        
        tailored_json_str = self.generate(prompt, system_prompt, temperature=0.5)
        
        # Extract JSON from response
        tailored_json_str = tailored_json_str.strip()
        if '```json' in tailored_json_str:
            tailored_json_str = tailored_json_str.split('```json')[1].split('```')[0].strip()
        elif '```' in tailored_json_str:
            tailored_json_str = tailored_json_str.split('```')[1].split('```')[0].strip()
        
        # Parse JSON
        try:
            tailored_data = json.loads(tailored_json_str)
        except json.JSONDecodeError as e:
            # Fallback: return original if JSON parsing fails
            print(f"Warning: Failed to parse AI response as JSON: {e}")
            return cv_html
        
        # Render JSON back to HTML using template
        # Load base template
        from app.storage import Storage
        storage = Storage()
        config = storage.load_config()
        template_path = storage.base_dir / config.get('cv_template_path', 'cv.html')
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template_html = f.read()
        
        # Render tailored data into template
        tailored_html = CVRenderer.render(template_html, tailored_data)
        
        return tailored_html
    
    def tailor_cv_with_answers(
        self,
        job_description: str,
        cv_html: str,
        skill_gap_answers: Dict,
        historical_cvs: Optional[List[Dict]] = None
    ) -> str:
        """
        Tailor CV content using skill gap answers from interactive questioning.
        
        Args:
            job_description: Target job description
            cv_html: Current CV HTML
            skill_gap_answers: Dict mapping skill names to answer dicts
            historical_cvs: Optional list of previous tailored CVs for context
        
        Returns:
            Tailored CV HTML
        """
        from app.cv_data import CVDataExtractor, CVRenderer
        
        # Extract CV data to JSON
        cv_data = CVDataExtractor.extract(cv_html)
        
        # Convert to JSON string for AI processing
        cv_json = json.dumps(cv_data, indent=2, ensure_ascii=False)
        
        # Build context from historical CVs
        historical_context = ""
        if historical_cvs:
            historical_context = "\n\nPrevious tailoring examples:\n"
            for hist in historical_cvs[:3]:
                historical_context += f"- {hist['company']} ({hist['job_title']}): Added skills {', '.join(hist.get('skills_added', []))}\n"
        
        # Build skill gap answers context
        answers_context = "\n\nUser's Experience with Missing Skills:\n"
        for skill, answer in skill_gap_answers.items():
            if answer.get('has_experience') is True:
                level = answer.get('experience_level', 'some')
                desc = answer.get('description', '')
                answers_context += f"- {skill}: Has {level} experience"
                if desc:
                    answers_context += f". Details: {desc}"
                answers_context += "\n"
            elif answer.get('has_experience') is False:
                related = answer.get('related_experience', '')
                if related:
                    answers_context += f"- {skill}: No direct experience, but has related experience: {related}\n"
                else:
                    answers_context += f"- {skill}: No direct experience\n"
        
        # Extract current summary for style reference
        current_summary = cv_data.get('summary', '')
        
        system_prompt = """You are a CV tailoring expert. You will receive CV data in JSON format.
        Your task is to modify ONLY the text content to better match the job description while maintaining accuracy and authenticity.
        Use the user's provided experience details to highlight relevant skills and frame their experience appropriately.
        
        IMPORTANT RULES:
        1. Return ONLY valid JSON - no markdown code blocks, no explanations
        2. Preserve the exact JSON structure - all keys, arrays, and object structure must remain the same
        3. Only modify text values (strings) - do NOT change structure, add/remove keys, or modify arrays in ways that break the format
        4. You CAN add items to arrays (e.g., add a new project, add skills to a skill group)
        5. Professional Summary Tailoring:
           - MUST tailor the professional summary to emphasize relevant experience based on user's answers
           - MAINTAIN the current writing style: concise, metrics-focused, uses strong action verbs
           - PRESERVE the structure: bold headings, specific numbers (e.g., "350+ engineers", "95%", "30%")
           - KEEP the authentic voice and tone - mimic the current style exactly
           - Use semantic understanding to highlight relevant experience, not just keyword matching
        6. Work experience bullets: incorporate user's experience descriptions naturally
        7. Skills section: ensure all relevant skills are visible (add missing ones to appropriate categories)
        8. For skills with related experience, frame them as transferable skills
        
        Return the complete JSON object with tailored content."""
        
        prompt = f"""Tailor this CV data to match the job description below, incorporating the user's experience details.

Job Description:
{job_description}

Current CV Data (JSON):
{cv_json}
{historical_context}
{answers_context}

Current Professional Summary Style Reference:
{current_summary}

IMPORTANT: When tailoring the professional summary:
- Analyze the current summary style above and mimic it exactly
- Keep the same structure: bold headings, metrics, concise paragraphs
- Maintain the authentic voice and writing tone
- Use semantic understanding to emphasize relevant experience for this job based on user's answers
- Do NOT change the writing style - only adjust content to be more relevant

Return the tailored CV data as valid JSON. Only modify text content to better match the job.
Use the user's experience details to:
- Highlight skills they have experience with
- Frame related experience appropriately
- Emphasize transferable skills where applicable
You can add new skills to existing skill groups, add new projects, or enhance descriptions.
Do NOT make up experience - only use what the user has provided.
Do NOT change the JSON structure or remove existing data."""
        
        tailored_json_str = self.generate(prompt, system_prompt, temperature=0.5)
        
        # Extract JSON from response
        tailored_json_str = tailored_json_str.strip()
        if '```json' in tailored_json_str:
            tailored_json_str = tailored_json_str.split('```json')[1].split('```')[0].strip()
        elif '```' in tailored_json_str:
            tailored_json_str = tailored_json_str.split('```')[1].split('```')[0].strip()
        
        # Parse JSON
        try:
            tailored_data = json.loads(tailored_json_str)
        except json.JSONDecodeError as e:
            # Fallback: return original if JSON parsing fails
            print(f"Warning: Failed to parse AI response as JSON: {e}")
            return cv_html
        
        # Render JSON back to HTML using template
        # Load base template
        from app.storage import Storage
        storage = Storage()
        config = storage.load_config()
        template_path = storage.base_dir / config.get('cv_template_path', 'cv.html')
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template_html = f.read()
        
        # Render tailored data into template
        tailored_html = CVRenderer.render(template_html, tailored_data)
        
        return tailored_html

