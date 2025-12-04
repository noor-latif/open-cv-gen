"""AI client using OpenAI SDK configured for Vercel AI Gateway."""

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
    
    def analyze_skill_gaps(self, required_skills: List[str], cv_skills: List[str]) -> Dict:
        """
        Analyze gaps between required skills and CV skills.
        
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
        from bs4 import BeautifulSoup
        
        # Parse CV HTML
        soup = BeautifulSoup(cv_html, 'html.parser')
        
        # Extract current content
        summary_section = soup.find('div', class_='ql-editor')
        if summary_section:
            current_summary = summary_section.get_text()[:500]
        else:
            current_summary = ""
        
        # Build context from historical CVs
        historical_context = ""
        if historical_cvs:
            historical_context = "\n\nPrevious tailoring examples:\n"
            for hist in historical_cvs[:3]:
                historical_context += f"- {hist['company']} ({hist['job_title']}): Added skills {', '.join(hist.get('skills_added', []))}\n"
        
        system_prompt = """You are a CV tailoring expert. Adapt the CV content to better match 
        the job description while maintaining accuracy and authenticity. Focus on:
        1. Professional summary - emphasize relevant experience
        2. Work experience bullets - highlight relevant achievements
        3. Skills section - ensure all relevant skills are visible
        
        Return the complete HTML with tailored content. Preserve all HTML structure, classes, and styling."""
        
        prompt = f"""Tailor this CV to match the job description below.

Job Description:
{job_description}

Current CV Summary (first 500 chars):
{current_summary}
{historical_context}

Return the complete HTML CV with tailored content. Keep all HTML structure, classes, IDs, and styling exactly as they are.
Only modify the text content (professional summary, work experience descriptions, skills) to better match the job.
Do not change any HTML tags, attributes, or structure."""
        
        tailored_html = self.generate(prompt, system_prompt, temperature=0.5)
        
        # Try to extract HTML from markdown code block if present
        if '```html' in tailored_html:
            tailored_html = tailored_html.split('```html')[1].split('```')[0].strip()
        elif '```' in tailored_html:
            tailored_html = tailored_html.split('```')[1].split('```')[0].strip()
        
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
        from bs4 import BeautifulSoup
        
        # Parse CV HTML
        soup = BeautifulSoup(cv_html, 'html.parser')
        
        # Extract current content
        summary_section = soup.find('div', class_='ql-editor')
        if summary_section:
            current_summary = summary_section.get_text()[:500]
        else:
            current_summary = ""
        
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
        
        system_prompt = """You are a CV tailoring expert. Adapt the CV content to better match 
        the job description while maintaining accuracy and authenticity. Use the user's provided 
        experience details to highlight relevant skills and frame their experience appropriately.
        
        Focus on:
        1. Professional summary - emphasize relevant experience based on user's answers
        2. Work experience bullets - incorporate user's experience descriptions naturally
        3. Skills section - ensure all relevant skills are visible
        4. For skills with related experience, frame them as transferable skills
        
        Return the complete HTML with tailored content. Preserve all HTML structure, classes, and styling."""
        
        prompt = f"""Tailor this CV to match the job description below, incorporating the user's experience details.

Job Description:
{job_description}

Current CV Summary (first 500 chars):
{current_summary}
{historical_context}
{answers_context}

Return the complete HTML CV with tailored content. Keep all HTML structure, classes, IDs, and styling exactly as they are.
Only modify the text content (professional summary, work experience descriptions, skills) to better match the job.
Use the user's experience details to:
- Highlight skills they have experience with
- Frame related experience appropriately
- Emphasize transferable skills where applicable
Do not make up experience - only use what the user has provided."""
        
        tailored_html = self.generate(prompt, system_prompt, temperature=0.5)
        
        # Try to extract HTML from markdown code block if present
        if '```html' in tailored_html:
            tailored_html = tailored_html.split('```html')[1].split('```')[0].strip()
        elif '```' in tailored_html:
            tailored_html = tailored_html.split('```')[1].split('```')[0].strip()
        
        return tailored_html

