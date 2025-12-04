"""Flask application initialization."""

from pathlib import Path

from flask import Flask

from app.storage import Storage


def create_app():
    """Create and configure Flask application."""
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    
    app = Flask(__name__, 
                template_folder=str(project_root / 'templates'),
                static_folder=str(project_root / 'static'))
    app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
    
    # Initialize storage
    storage = Storage()
    app.storage = storage
    
    # Initialize AI client and CV engine (lazy loading)
    app.ai_client = None
    app.cv_engine = None
    
    # Register routes
    from app import routes
    app.register_blueprint(routes.bp)
    
    return app

