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
    
    def extract_cv_skills(self, cv_html: str) -> List[str]:
        """Extract skills from CV HTML."""
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
        Analyze skill gaps between job description and CV.
        
        Returns:
            Dict with 'required_skills', 'cv_skills', 'gaps', 'suggestions'
        """
        # Extract skills from job description
        required_skills = self.ai_client.extract_skills(job_description)
        
        # Extract skills from CV
        cv_skills = self.extract_cv_skills(cv_html)
        
        # Analyze gaps
        gap_analysis = self.ai_client.analyze_skill_gaps(required_skills, cv_skills)
        
        return {
            'required_skills': required_skills,
            'cv_skills': cv_skills,
            'missing_skills': gap_analysis['missing'],
            'present_skills': gap_analysis['present'],
            'suggestions': gap_analysis['suggestions']
        }
    
    def add_skills_to_cv(self, cv_html: str, new_skills: List[str], skill_category: str = "Technical Skills") -> str:
        """
        Add new skills to CV HTML.
        
        Args:
            cv_html: Current CV HTML
            new_skills: List of new skills to add
            skill_category: Category to add skills to (default: "Technical Skills")
        
        Returns:
            Updated CV HTML
        """
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(cv_html, 'html.parser')
        
        # Find the skill category
        skill_groups = soup.find_all('div', class_='skill-group')
        target_group = None
        
        for group in skill_groups:
            title = group.find('div', class_='skill-group-title')
            if title and skill_category.lower() in title.get_text().lower():
                target_group = group
                break
        
        # If category not found, use first Technical Skills group
        if not target_group:
            for group in skill_groups:
                title = group.find('div', class_='skill-group-title')
                if title and 'technical' in title.get_text().lower():
                    target_group = group
                    break
        
        # If still not found, use first skill group
        if not target_group and skill_groups:
            target_group = skill_groups[0]
        
        if target_group:
            skill_tags_div = target_group.find('div', class_='skill-tags')
            if skill_tags_div:
                # Add new skills
                for skill in new_skills:
                    if skill.strip():
                        new_tag = soup.new_tag('span', class_='skill-tag')
                        new_tag.string = skill.strip()
                        skill_tags_div.append(new_tag)
        
        return str(soup)


