"""Flask routes for CV dashboard."""

import asyncio
import sys
from pathlib import Path

from flask import Blueprint, flash, redirect, render_template, request, send_file, session, url_for

# Add parent directory to path for html_to_pdf import
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.ai_client import AIClient
from app.cv_engine import CVEngine
from app.storage import Storage
from html_to_pdf import html_to_pdf

bp = Blueprint('cv', __name__)


def get_cv_engine():
    """Get or initialize CV engine."""
    from flask import current_app
    
    if current_app.cv_engine is None:
        config = current_app.storage.load_config()
        ai_client = AIClient(config)
        current_app.ai_client = ai_client
        current_app.cv_engine = CVEngine(ai_client, current_app.storage)
    
    return current_app.cv_engine


@bp.route('/')
def dashboard():
    """Main dashboard showing application history."""
    storage = Storage()
    applications = storage.list_applications()
    return render_template('dashboard.html', applications=applications)


@bp.route('/generate', methods=['GET', 'POST'])
def generate():
    """Generate tailored CV."""
    if request.method == 'GET':
        return render_template('generate.html')
    
    # POST request - generate CV
    job_description = request.form.get('job_description', '').strip()
    company = request.form.get('company', '').strip()
    job_title = request.form.get('job_title', '').strip()
    
    if not job_description:
        flash('Job description is required', 'error')
        return redirect(url_for('cv.generate'))
    
    try:
        cv_engine = get_cv_engine()
        
        # Get skills to add from form
        add_skills_str = request.form.get('add_skills', '')
        add_skills = [s.strip() for s in add_skills_str.split(',') if s.strip()] if add_skills_str else []
        
        # Generate tailored CV
        result = cv_engine.generate_tailored_cv(
            job_description=job_description,
            company=company,
            job_title=job_title,
            add_skills=add_skills if add_skills else None
        )
        
        # Check if there are skill gaps
        skill_gaps = result['skill_gaps']
        
        # If there are gaps and no skills were added, start interactive questioning
        if skill_gaps and not add_skills:
            # Store in session for interactive questioning
            session['cv_generation'] = {
                'job_description': job_description,
                'company': company or 'Unknown',
                'job_title': job_title or 'Unknown',
                'skill_gaps': skill_gaps,
                'suggestions': result['analysis']['suggestions'],
                'analysis': result['analysis'],
                'answers': {},
                'current_skill_index': 0
            }
            return redirect(url_for('cv.questions'))
        
        # Save application record first to get app_id
        application_data = {
            'company': company or 'Unknown',
            'job_title': job_title or 'Unknown',
            'job_description': job_description,
            'cv_html': result['cv_html'],
            'cv_pdf_path': None,
            'skill_gaps': skill_gaps,
            'skills_added': add_skills if add_skills else []  # Store empty list, not None
        }
        
        app_id = cv_engine.storage.save_application(application_data)
        
        # Save CV HTML with app_id
        cv_file = cv_engine.storage.save_cv_html(app_id, result['cv_html'])
        
        # Generate PDF
        pdf_path = None
        try:
            pdf_output = cv_engine.storage.cv_history_dir / f"{app_id}.pdf"
            asyncio.run(html_to_pdf(str(cv_file), str(pdf_output)))
            pdf_path = str(pdf_output)
            
            # Update application with PDF path
            cv_engine.storage.update_application(app_id, {'cv_pdf_path': pdf_path})
        except Exception as e:
            flash(f'PDF generation failed: {str(e)}', 'warning')
        
        flash('CV generated successfully!', 'success')
        return redirect(url_for('cv.application', app_id=app_id))
    
    except Exception as e:
        flash(f'Error generating CV: {str(e)}', 'error')
        return render_template('generate.html', 
                             job_description=job_description,
                             company=company,
                             job_title=job_title)


@bp.route('/application/<app_id>')
def application(app_id):
    """View application details."""
    storage = Storage()
    app_data = storage.load_application(app_id)
    
    if not app_data:
        flash('Application not found', 'error')
        return redirect(url_for('cv.dashboard'))
    
    return render_template('application.html', application=app_data)


@bp.route('/application/<app_id>/update-skills', methods=['POST'])
def update_skills(app_id):
    """Update application with additional skills."""
    storage = Storage()
    app_data = storage.load_application(app_id)
    
    if not app_data:
        flash('Application not found', 'error')
        return redirect(url_for('cv.dashboard'))
    
    add_skills_str = request.form.get('add_skills', '')
    add_skills = [s.strip() for s in add_skills_str.split(',') if s.strip()] if add_skills_str else []
    
    if add_skills:
        from app.skill_analyzer import SkillAnalyzer
        from app.ai_client import AIClient
        
        config = storage.load_config()
        ai_client = AIClient(config)
        skill_analyzer = SkillAnalyzer(ai_client, storage)
        
        # Add skills to CV
        updated_cv = skill_analyzer.add_skills_to_cv(app_data['cv_html'], add_skills)
        
        # Update application
        # Handle case where skills_added might be None (from empty list conversion)
        existing_skills = app_data.get('skills_added') or []
        storage.update_application(app_id, {
            'cv_html': updated_cv,
            'skills_added': existing_skills + add_skills
        })
        
        # Regenerate PDF
        try:
            cv_engine = get_cv_engine()
            cv_file = cv_engine.storage.cv_history_dir / f"{app_id}.html"
            cv_file.write_text(updated_cv, encoding='utf-8')
            
            pdf_output = cv_engine.storage.cv_history_dir / f"{app_id}.pdf"
            asyncio.run(html_to_pdf(str(cv_file), str(pdf_output)))
            
            storage.update_application(app_id, {
                'cv_pdf_path': str(pdf_output)
            })
        except Exception as e:
            flash(f'PDF regeneration failed: {str(e)}', 'warning')
        
        flash('Skills added successfully!', 'success')
    
    return redirect(url_for('cv.application', app_id=app_id))


@bp.route('/application/<app_id>/pdf')
def download_pdf(app_id):
    """Download PDF for application."""
    storage = Storage()
    app_data = storage.load_application(app_id)
    
    if not app_data or not app_data.get('cv_pdf_path'):
        flash('PDF not found', 'error')
        return redirect(url_for('cv.application', app_id=app_id))
    
    pdf_path = Path(app_data['cv_pdf_path'])
    if not pdf_path.exists():
        flash('PDF file not found', 'error')
        return redirect(url_for('cv.application', app_id=app_id))
    
    return send_file(pdf_path, as_attachment=True, download_name=f"cv_{app_id}.pdf")


@bp.route('/generate/questions', methods=['GET', 'POST'])
def questions():
    """Interactive skill gap questioning."""
    # Check if session data exists
    if 'cv_generation' not in session:
        flash('Please start by submitting a job description', 'error')
        return redirect(url_for('cv.generate'))
    
    gen_data = session['cv_generation']
    skill_gaps = gen_data['skill_gaps']
    current_index = gen_data.get('current_skill_index', 0)
    
    # Ensure answers dict exists
    if 'answers' not in gen_data:
        gen_data['answers'] = {}
    
    if request.method == 'POST':
        # Save answer for current skill
        current_skill = skill_gaps[current_index]
        has_experience_val = request.form.get('has_experience')
        
        # If no answer provided, treat as skip
        if not has_experience_val:
            has_experience_val = 'skip'
        
        # Handle skip option
        if has_experience_val == 'skip':
            gen_data['answers'][current_skill] = {
                'has_experience': None,
                'experience_level': '',
                'description': '',
                'related_experience': ''
            }
        else:
            has_experience = has_experience_val == 'yes'
            experience_level = request.form.get('experience_level', '')
            description = request.form.get('description', '').strip()
            related_experience = request.form.get('related_experience', '').strip()
            
            # Save answer
            gen_data['answers'][current_skill] = {
                'has_experience': has_experience,
                'experience_level': experience_level,
                'description': description,
                'related_experience': related_experience
            }
        
        # Move to next skill or finalize
        if current_index < len(skill_gaps) - 1:
            gen_data['current_skill_index'] = current_index + 1
            session['cv_generation'] = gen_data
            return redirect(url_for('cv.questions'))
        else:
            # All questions answered, redirect to finalize
            session['cv_generation'] = gen_data
            return redirect(url_for('cv.finalize'))
    
    # GET request - show current question
    if current_index >= len(skill_gaps):
        # All questions answered, go to finalize
        return redirect(url_for('cv.finalize'))
    
    current_skill = skill_gaps[current_index]
    existing_answer = gen_data.get('answers', {}).get(current_skill, {})
    
    return render_template(
        'questions.html',
        skill=current_skill,
        skill_index=current_index + 1,
        total_skills=len(skill_gaps),
        suggestions=gen_data.get('suggestions', ''),
        existing_answer=existing_answer,
        can_go_back=current_index > 0
    )


@bp.route('/generate/questions/previous', methods=['POST'])
def questions_previous():
    """Go back to previous question."""
    if 'cv_generation' not in session:
        return redirect(url_for('cv.generate'))
    
    gen_data = session['cv_generation']
    current_index = gen_data.get('current_skill_index', 0)
    
    if current_index > 0:
        gen_data['current_skill_index'] = current_index - 1
        session['cv_generation'] = gen_data
    
    return redirect(url_for('cv.questions'))


@bp.route('/generate/finalize', methods=['GET', 'POST'])
def finalize():
    """Generate CV with all collected answers."""
    if 'cv_generation' not in session:
        flash('Please start by submitting a job description', 'error')
        return redirect(url_for('cv.generate'))
    
    gen_data = session['cv_generation']
    skill_gaps = gen_data['skill_gaps']
    
    if request.method == 'GET':
        # Show summary before generating
        return render_template(
            'finalize.html',
            job_description=gen_data['job_description'],
            company=gen_data['company'],
            job_title=gen_data['job_title'],
            skill_gaps=gen_data['skill_gaps'],
            answers=gen_data.get('answers', {})
        )
    
    # POST - Generate CV
    try:
        cv_engine = get_cv_engine()
        
        # Generate CV with answers
        result = cv_engine.generate_tailored_cv_with_answers(
            job_description=gen_data['job_description'],
            company=gen_data['company'],
            job_title=gen_data['job_title'],
            skill_gap_answers=gen_data['answers']
        )
        
        # Save application record
        application_data = {
            'company': gen_data['company'],
            'job_title': gen_data['job_title'],
            'job_description': gen_data['job_description'],
            'cv_html': result['cv_html'],
            'cv_pdf_path': None,
            'skill_gaps': gen_data['skill_gaps'],
            'skill_gap_answers': gen_data['answers'],
            'skills_added': []  # Skills added through answers
        }
        
        app_id = cv_engine.storage.save_application(application_data)
        
        # Save CV HTML
        cv_file = cv_engine.storage.save_cv_html(app_id, result['cv_html'])
        
        # Generate PDF
        pdf_path = None
        try:
            pdf_output = cv_engine.storage.cv_history_dir / f"{app_id}.pdf"
            asyncio.run(html_to_pdf(str(cv_file), str(pdf_output)))
            pdf_path = str(pdf_output)
            cv_engine.storage.update_application(app_id, {'cv_pdf_path': pdf_path})
        except Exception as e:
            flash(f'PDF generation failed: {str(e)}', 'warning')
        
        # Clear session
        session.pop('cv_generation', None)
        
        flash('CV generated successfully!', 'success')
        return redirect(url_for('cv.application', app_id=app_id))
    
    except Exception as e:
        flash(f'Error generating CV: {str(e)}', 'error')
        return redirect(url_for('cv.finalize'))

