"""CV tailoring engine."""

from typing import Dict, List, Optional

from app.ai_client import AIClient
from app.skill_analyzer import SkillAnalyzer
from app.storage import Storage


class CVEngine:
    """Main engine for CV tailoring."""
    
    def __init__(self, ai_client: AIClient, storage: Storage):
        """Initialize CV engine."""
        self.ai_client = ai_client
        self.storage = storage
        self.skill_analyzer = SkillAnalyzer(ai_client, storage)
    
    def load_base_cv(self) -> str:
        """Load base CV template."""
        config = self.storage.load_config()
        cv_path = self.storage.base_dir / config.get('cv_template_path', 'cv.html')
        
        if not cv_path.exists():
            raise FileNotFoundError(f"CV template not found: {cv_path}")
        
        with open(cv_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def generate_tailored_cv(
        self,
        job_description: str,
        company: str = "",
        job_title: str = "",
        add_skills: Optional[List[str]] = None
    ) -> Dict:
        """
        Generate a tailored CV for a job description.
        
        Args:
            job_description: Target job description
            company: Company name (optional)
            job_title: Job title (optional)
            add_skills: Optional list of additional skills to add
        
        Returns:
            Dict with 'cv_html', 'skill_gaps', 'analysis'
        """
        # Load base CV
        base_cv = self.load_base_cv()
        
        # Get historical CVs for context
        historical_cvs = self.storage.get_historical_cvs(limit=3)
        
        # Analyze skill gaps
        analysis = self.skill_analyzer.analyze(job_description, base_cv)
        
        # Add any provided skills
        if add_skills:
            base_cv = self.skill_analyzer.add_skills_to_cv(base_cv, add_skills)
            # Re-analyze after adding skills
            analysis = self.skill_analyzer.analyze(job_description, base_cv)
        
        # Tailor CV using AI
        tailored_cv = self.ai_client.tailor_cv(job_description, base_cv, historical_cvs)
        
        return {
            'cv_html': tailored_cv,
            'skill_gaps': analysis['missing_skills'],
            'analysis': analysis,
            'company': company,
            'job_title': job_title,
            'job_description': job_description
        }
    
    def generate_tailored_cv_with_answers(
        self,
        job_description: str,
        company: str = "",
        job_title: str = "",
        skill_gap_answers: Dict = None
    ) -> Dict:
        """
        Generate a tailored CV using skill gap answers from interactive questioning.
        
        Args:
            job_description: Target job description
            company: Company name (optional)
            job_title: Job title (optional)
            skill_gap_answers: Dict mapping skill names to answer dicts with:
                - has_experience: bool
                - experience_level: str (beginner/intermediate/advanced)
                - description: str
                - related_experience: str
        
        Returns:
            Dict with 'cv_html', 'skill_gaps', 'analysis'
        """
        # Load base CV
        base_cv = self.load_base_cv()
        
        # Get historical CVs for context
        historical_cvs = self.storage.get_historical_cvs(limit=3)
        
        # Analyze skill gaps (for reference, but we'll use answers)
        analysis = self.skill_analyzer.analyze(job_description, base_cv)
        
        # Extract skills that user has experience with to add to CV
        skills_to_add = []
        for skill, answer in (skill_gap_answers or {}).items():
            if answer.get('has_experience') is True:
                skills_to_add.append(skill)
            elif answer.get('has_experience') is False and answer.get('related_experience'):
                # Add related skills mentioned
                skills_to_add.append(skill)
        
        # Add skills to CV
        if skills_to_add:
            base_cv = self.skill_analyzer.add_skills_to_cv(base_cv, skills_to_add)
        
        # Tailor CV using AI with answers context
        tailored_cv = self.ai_client.tailor_cv_with_answers(
            job_description=job_description,
            cv_html=base_cv,
            skill_gap_answers=skill_gap_answers or {},
            historical_cvs=historical_cvs
        )
        
        return {
            'cv_html': tailored_cv,
            'skill_gaps': analysis['missing_skills'],
            'analysis': analysis,
            'company': company,
            'job_title': job_title,
            'job_description': job_description
        }


