"""JSON-based storage operations for applications and CV history."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class Storage:
    """Manages JSON-based storage for applications and CV history."""
    
    def __init__(self, base_dir: Path = None):
        """Initialize storage with base directory."""
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        self.base_dir = base_dir
        self.applications_dir = base_dir / "applications"
        self.cv_history_dir = base_dir / "cv_history"
        self.config_file = base_dir / "config.json"
        
        # Create directories if they don't exist
        self.applications_dir.mkdir(exist_ok=True)
        self.cv_history_dir.mkdir(exist_ok=True)
        
        # Initialize config if it doesn't exist
        if not self.config_file.exists():
            self._init_config()
    
    def _init_config(self):
        """Initialize default config file."""
        default_config = {
            "ai": {
                "gateway_url": "",
                "api_key": "",
                "model": "gpt-4"
            },
            "cv_template_path": "cv.html"
        }
        self.save_config(default_config)
    
    def save_config(self, config: Dict):
        """Save configuration to config.json."""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def load_config(self) -> Dict:
        """Load configuration from config.json."""
        if not self.config_file.exists():
            self._init_config()
        with open(self.config_file, 'r') as f:
            return json.load(f)
    
    def save_application(self, application_data: Dict) -> str:
        """
        Save application data to JSON file.
        
        Returns:
            Application ID (filename without extension)
        """
        # Generate ID from company name and timestamp
        company = application_data.get('company', 'unknown').lower().replace(' ', '_')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        app_id = f"{company}_{timestamp}"
        
        # Add timestamps if not present
        if 'created_at' not in application_data:
            application_data['created_at'] = datetime.now().isoformat()
        application_data['updated_at'] = datetime.now().isoformat()
        application_data['id'] = app_id
        
        # Save to applications directory
        app_file = self.applications_dir / f"{app_id}.json"
        with open(app_file, 'w') as f:
            json.dump(application_data, f, indent=2)
        
        return app_id
    
    def load_application(self, app_id: str) -> Optional[Dict]:
        """Load application data by ID."""
        app_file = self.applications_dir / f"{app_id}.json"
        if not app_file.exists():
            return None
        with open(app_file, 'r') as f:
            return json.load(f)
    
    def list_applications(self) -> List[Dict]:
        """List all applications, sorted by created_at (newest first)."""
        applications = []
        for app_file in self.applications_dir.glob("*.json"):
            with open(app_file, 'r') as f:
                app_data = json.load(f)
                applications.append(app_data)
        
        # Sort by created_at, newest first
        applications.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return applications
    
    def update_application(self, app_id: str, updates: Dict) -> bool:
        """Update application data."""
        app_data = self.load_application(app_id)
        if app_data is None:
            return False
        
        app_data.update(updates)
        app_data['updated_at'] = datetime.now().isoformat()
        
        app_file = self.applications_dir / f"{app_id}.json"
        with open(app_file, 'w') as f:
            json.dump(app_data, f, indent=2)
        
        return True
    
    def save_cv_html(self, app_id: str, cv_html: str) -> Path:
        """Save CV HTML to cv_history directory."""
        cv_file = self.cv_history_dir / f"{app_id}.html"
        with open(cv_file, 'w', encoding='utf-8') as f:
            f.write(cv_html)
        return cv_file
    
    def load_cv_html(self, app_id: str) -> Optional[str]:
        """Load CV HTML from cv_history directory."""
        cv_file = self.cv_history_dir / f"{app_id}.html"
        if not cv_file.exists():
            return None
        with open(cv_file, 'r', encoding='utf-8') as f:
            return f.read()
    
    def get_cv_file_path(self, app_id: str) -> Path:
        """Get the file path for a CV HTML file."""
        return self.cv_history_dir / f"{app_id}.html"
    
    def get_historical_cvs(self, limit: int = 5) -> List[Dict]:
        """Get recent CVs for learning context."""
        applications = self.list_applications()
        historical = []
        for app in applications[:limit]:
            cv_html = self.load_cv_html(app['id'])
            if cv_html:
                historical.append({
                    'id': app['id'],
                    'company': app.get('company', ''),
                    'job_title': app.get('job_title', ''),
                    'cv_html': cv_html,
                    'skills_added': app.get('skills_added', [])
                })
        return historical

