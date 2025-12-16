"""Skill gap analysis module."""

from typing import Dict, List

from app.ai_client import AIClient
from app.storage import Storage


class SkillAnalyzer:
    """Analyzes skill gaps between CV and job requirements."""
    
    def __init__(self, ai_client: AIClient, storage: Storage):
        """Initialize skill analyzer."""
        self.ai_client = ai_client
        self.storage = storage
    
    def _extract_cv_text(self, cv_html: str) -> str:
        """
        Extract all visible text content from CV HTML.
        
        Args:
            cv_html: CV HTML content
        
        Returns:
            Full text content of the CV
        """
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(cv_html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get all text content
        cv_text = soup.get_text(separator=' ', strip=True)
        
        return cv_text
    
    def extract_cv_skills(self, cv_html: str) -> List[str]:
        """
        Extract skills from CV HTML.
        
        NOTE: This method is kept for backward compatibility. The new semantic analysis
        approach in analyze() is preferred as it understands context and synonyms.
        
        Returns:
            List of skill names from skill-tags
        """
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(cv_html, 'html.parser')
        skills = []
        
        # Find all skill tags
        skill_tags = soup.find_all('span', class_='skill-tag')
        for tag in skill_tags:
            skill_text = tag.get_text().strip()
            if skill_text:
                skills.append(skill_text)
        
        return skills
    
    def analyze(self, job_description: str, cv_html: str) -> Dict:
        """
        Analyze CV-job alignment using semantic understanding.
        
        This method uses AI to semantically analyze how well a CV matches a job description,
        understanding context, synonyms, and related terms rather than simple keyword matching.
        
        Args:
            job_description: Target job description
            cv_html: Current CV HTML
        
        Returns:
            Dict with:
                - required_skills: Key skills/requirements from job description
                - cv_skills: Skills/experience from CV that match job (with context)
                - missing_skills: True gaps where CV genuinely lacks required experience
                - present_skills: Experience in CV that matches job requirements
                - suggestions: How to highlight existing experience or address gaps
        """
        # Extract full CV text (all visible content including professional summary,
        # experience descriptions, education titles, certification titles, etc.)
        cv_text = self._extract_cv_text(cv_html)
        
        # Use AI for semantic analysis instead of skill extraction
        analysis = self.ai_client.analyze_cv_job_alignment(cv_text, job_description)
        
        return {
            'required_skills': analysis.get('required_skills', []),
            'cv_skills': analysis.get('relevant_experience', []),
            'missing_skills': analysis.get('gaps', []),
            'present_skills': analysis.get('matched_experience', []),
            'suggestions': analysis.get('suggestions', '')
        }
    
    def add_skills_to_cv(self, cv_html: str, new_skills: List[str], skill_category: str = "Technical Skills") -> str:
        """
        Add new skills to CV HTML using JSON-based approach.
        
        Args:
            cv_html: Current CV HTML
            new_skills: List of new skills to add
            skill_category: Category to add skills to (default: "Technical Skills")
        
        Returns:
            Updated CV HTML
        """
        from app.cv_data import CVDataExtractor, CVRenderer
        from app.storage import Storage
        
        # Extract CV data to JSON
        cv_data = CVDataExtractor.extract(cv_html)
        
        # Find the target skill category and add skills
        target_group = None
        for skill_group in cv_data.get('skills', []):
            if skill_category.lower() in skill_group.get('category', '').lower():
                target_group = skill_group
                break
        
        # If category not found, use first Technical Skills group
        if not target_group:
            for skill_group in cv_data.get('skills', []):
                if 'technical' in skill_group.get('category', '').lower():
                    target_group = skill_group
                    break
        
        # If still not found, use first skill group
        if not target_group and cv_data.get('skills'):
            target_group = cv_data['skills'][0]
        
        # Add new skills to the target group
        if target_group:
            existing_items = set(target_group.get('items', []))
            for skill in new_skills:
                skill_clean = skill.strip()
                if skill_clean and skill_clean not in existing_items:
                    target_group.setdefault('items', []).append(skill_clean)
        
        # Render back to HTML using template
        storage = Storage()
        config = storage.load_config()
        template_path = storage.base_dir / config.get('cv_template_path', 'cv.html')
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template_html = f.read()
        
        # Render updated data into template
        updated_html = CVRenderer.render(template_html, cv_data)
        
        return updated_html


