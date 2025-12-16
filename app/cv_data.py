"""CV data extraction and rendering module for JSON-based content management."""

import json
from typing import Dict, List, Optional
from bs4 import BeautifulSoup


class CVDataExtractor:
    """Extracts structured data from CV HTML template."""
    
    @staticmethod
    def extract(cv_html: str) -> Dict:
        """
        Extract structured data from CV HTML.
        
        Returns:
            Dict with all CV content in structured format
        """
        soup = BeautifulSoup(cv_html, 'html.parser')
        
        data = {
            'profile': CVDataExtractor._extract_profile(soup),
            'contact': CVDataExtractor._extract_contact(soup),
            'links': CVDataExtractor._extract_links(soup),
            'skills': CVDataExtractor._extract_skills(soup),
            'languages': CVDataExtractor._extract_languages(soup),
            'summary': CVDataExtractor._extract_summary(soup),
            'experience': CVDataExtractor._extract_experience(soup),
            'education': CVDataExtractor._extract_education(soup),
            'projects': CVDataExtractor._extract_projects(soup),
            'certifications': CVDataExtractor._extract_certifications(soup)
        }
        
        return data
    
    @staticmethod
    def _extract_profile(soup: BeautifulSoup) -> Dict:
        """Extract profile information."""
        profile = {}
        
        # Name
        h1 = soup.find('h1')
        if h1:
            profile['name'] = h1.get_text().strip()
        
        # Title
        title_p = soup.find('p', style=lambda x: x and 'font-size:1.25rem' in x)
        if title_p:
            profile['title'] = title_p.get_text().strip()
        
        # Profile image
        img = soup.find('img', alt=lambda x: x and 'Noor' in x)
        if img:
            profile['image'] = img.get('src', '')
        
        return profile
    
    @staticmethod
    def _extract_contact(soup: BeautifulSoup) -> Dict:
        """Extract contact information."""
        contact = {}
        
        contact_items = soup.find_all('div', class_='contact-item')
        for item in contact_items:
            icon = item.find('svg')
            if icon:
                # Determine type by SVG path or parent structure
                text = item.get_text().strip()
                if 'phone' in str(icon) or '+46' in text:
                    contact['phone'] = text
                elif 'mail' in str(icon) or '@' in text:
                    contact['email'] = text
                elif 'house' in str(icon) or 'Gothenburg' in text or 'Stockholm' in text:
                    contact['location'] = text
        
        return contact
    
    @staticmethod
    def _extract_links(soup: BeautifulSoup) -> List[Dict]:
        """Extract links."""
        links = []
        
        link_items = soup.find_all('div', class_='contact-item')
        for item in link_items:
            a_tag = item.find('a')
            if a_tag:
                links.append({
                    'text': a_tag.get_text().strip(),
                    'url': a_tag.get('href', '')
                })
        
        return links
    
    @staticmethod
    def _extract_skills(soup: BeautifulSoup) -> List[Dict]:
        """Extract skills grouped by category."""
        skills = []
        
        skill_groups = soup.find_all('div', class_='skill-group')
        for group in skill_groups:
            title_elem = group.find('div', class_='skill-group-title')
            if title_elem:
                category = title_elem.get_text().strip()
                skill_tags = group.find_all('span', class_='skill-tag')
                skill_list = [tag.get_text().strip() for tag in skill_tags]
                
                skills.append({
                    'category': category,
                    'items': skill_list
                })
        
        return skills
    
    @staticmethod
    def _extract_languages(soup: BeautifulSoup) -> List[Dict]:
        """Extract languages with proficiency."""
        languages = []
        
        # Find languages section
        languages_section = None
        for h2 in soup.find_all('h2'):
            if h2.get_text().strip() == 'Languages':
                languages_section = h2.find_parent('div', class_='space-y-3')
                break
        
        if languages_section:
            lang_items = languages_section.find_all('div', class_='space-y-1')
            for item in lang_items:
                lang_name_elem = item.find('span', class_='text-sm')
                if lang_name_elem:
                    lang_name = lang_name_elem.get_text().strip()
                    # Find proficiency from language-bar-fill width
                    bar_fill = item.find('div', class_='language-bar-fill')
                    proficiency = 100
                    if bar_fill:
                        style = bar_fill.get('style', '')
                        if 'width:' in style:
                            try:
                                proficiency = int(style.split('width:')[1].split('%')[0])
                            except:
                                pass
                    
                    languages.append({
                        'name': lang_name,
                        'proficiency': proficiency
                    })
        
        return languages
    
    @staticmethod
    def _extract_summary(soup: BeautifulSoup) -> str:
        """Extract professional summary."""
        # Find Professional Summary section
        summary_section = None
        for h2 in soup.find_all('h2'):
            if h2.get_text().strip() == 'Professional Summary':
                parent = h2.find_parent('div', class_='space-y-3')
                if parent:
                    summary_section = parent.find('div', class_='ql-editor')
                    break
        
        if summary_section:
            # Get all paragraphs and preserve their structure
            paragraphs = summary_section.find_all('p')
            summary_parts = []
            for p in paragraphs:
                # Preserve bold text with ** markers
                text = p.get_text()
                # Check if paragraph has strong tags
                strong_tags = p.find_all('strong')
                if strong_tags:
                    # Reconstruct with ** markers
                    parts = []
                    for content in p.contents:
                        if hasattr(content, 'name') and content.name == 'strong':
                            parts.append(f"**{content.get_text()}**")
                        elif isinstance(content, str):
                            parts.append(content)
                    text = ''.join(parts)
                summary_parts.append(text.strip())
            return '\n\n'.join(summary_parts)
        
        return ""
    
    @staticmethod
    def _extract_experience(soup: BeautifulSoup) -> List[Dict]:
        """Extract work experience."""
        experience = []
        
        # Find work experience section
        experience_section = None
        for h2 in soup.find_all('h2'):
            if h2.get_text().strip() == 'Work Experience':
                experience_section = h2.find_parent('div', class_='space-y-3')
                break
        
        if experience_section:
            timeline_items = experience_section.find_all('div', class_='timeline-item')
            for item in timeline_items:
                exp = {}
                
                # Title
                h3 = item.find('h3')
                if h3:
                    exp['title'] = h3.get_text().strip()
                
                # Date
                date_badge = item.find('span', class_='date-badge')
                if date_badge:
                    exp['date'] = date_badge.get_text().strip()
                
                # Company and location
                company_p = item.find('p', class_='text-sm')
                if company_p:
                    exp['company'] = company_p.get_text().strip()
                
                location_p = item.find('p', class_='text-xs')
                if location_p:
                    exp['location'] = location_p.get_text().strip()
                
                # Description
                ql_editor = item.find('div', class_='ql-editor')
                if ql_editor:
                    # Extract paragraphs (excluding Key Technologies)
                    paragraphs = ql_editor.find_all('p')
                    exp['description'] = []
                    for p in paragraphs:
                        text = p.get_text().strip()
                        if 'Key Technologies' not in text and text:
                            exp['description'].append(text)
                    
                    # Extract bullet points
                    bullets = ql_editor.find_all('li', attrs={'data-list': 'bullet'})
                    exp['bullets'] = []
                    for bullet in bullets:
                        bullet_text = bullet.get_text().strip()
                        if bullet_text:
                            exp['bullets'].append(bullet_text)
                    
                    # Key technologies
                    tech_p = None
                    for p in paragraphs:
                        if 'Key Technologies' in p.get_text():
                            tech_p = p
                            break
                    if tech_p:
                        exp['technologies'] = tech_p.get_text().replace('Key Technologies:', '').replace('Key Technologies', '').strip()
                
                experience.append(exp)
        
        return experience
    
    @staticmethod
    def _extract_education(soup: BeautifulSoup) -> List[Dict]:
        """Extract education."""
        education = []
        
        # Find education section
        education_section = None
        for h2 in soup.find_all('h2'):
            if h2.get_text().strip() == 'Education':
                education_section = h2.find_parent('div', class_='space-y-3')
                break
        
        if education_section:
            timeline_items = education_section.find_all('div', class_='timeline-item')
            for item in timeline_items:
                edu = {}
                
                h3 = item.find('h3')
                if h3:
                    edu['degree'] = h3.get_text().strip()
                
                date_badge = item.find('span', class_='date-badge')
                if date_badge:
                    edu['date'] = date_badge.get_text().strip()
                
                company_p = item.find('p', class_='text-sm')
                if company_p:
                    edu['institution'] = company_p.get_text().strip()
                
                location_p = item.find('p', class_='text-xs')
                if location_p:
                    edu['location'] = location_p.get_text().strip()
                
                ql_editor = item.find('div', class_='ql-editor')
                if ql_editor:
                    p = ql_editor.find('p')
                    if p:
                        edu['description'] = p.get_text().strip()
                
                education.append(edu)
        
        return education
    
    @staticmethod
    def _extract_projects(soup: BeautifulSoup) -> List[Dict]:
        """Extract projects."""
        projects = []
        
        # Find projects section
        projects_section = None
        for h2 in soup.find_all('h2'):
            if h2.get_text().strip() == 'Projects':
                projects_section = h2.find_parent('div', class_='space-y-3')
                break
        
        if projects_section:
            timeline_items = projects_section.find_all('div', class_='timeline-item')
            for item in timeline_items:
                proj = {}
                
                h3 = item.find('h3')
                if h3:
                    a_tag = h3.find('a')
                    if a_tag:
                        proj['title'] = a_tag.get_text().strip()
                        proj['url'] = a_tag.get('href', '')
                    else:
                        proj['title'] = h3.get_text().strip()
                
                date_badge = item.find('span', class_='date-badge')
                if date_badge:
                    proj['date'] = date_badge.get_text().strip()
                
                ql_editor = item.find('div', class_='ql-editor')
                if ql_editor:
                    paragraphs = ql_editor.find_all('p')
                    if paragraphs:
                        proj['description'] = paragraphs[0].get_text().strip()
                    
                    bullets = ql_editor.find_all('li', attrs={'data-list': 'bullet'})
                    proj['bullets'] = []
                    for bullet in bullets:
                        bullet_text = bullet.get_text().strip()
                        if bullet_text:
                            proj['bullets'].append(bullet_text)
                    
                    # Key technologies
                    for p in paragraphs:
                        if 'Key Technologies' in p.get_text():
                            proj['technologies'] = p.get_text().replace('Key Technologies:', '').strip()
                            break
                
                projects.append(proj)
        
        return projects
    
    @staticmethod
    def _extract_certifications(soup: BeautifulSoup) -> List[Dict]:
        """Extract certifications."""
        certifications = []
        
        # Find certifications section
        cert_section = None
        for h2 in soup.find_all('h2'):
            if h2.get_text().strip() == 'Certifications':
                cert_section = h2.find_parent('div', class_='space-y-3')
                break
        
        if cert_section:
            timeline_items = cert_section.find_all('div', class_='timeline-item')
            for item in timeline_items:
                cert = {}
                
                h3 = item.find('h3')
                if h3:
                    a_tag = h3.find('a')
                    if a_tag:
                        cert['title'] = a_tag.get_text().strip()
                        cert['url'] = a_tag.get('href', '')
                    else:
                        cert['title'] = h3.get_text().strip()
                
                date_badge = item.find('span', class_='date-badge')
                if date_badge:
                    cert['date'] = date_badge.get_text().strip()
                
                company_p = item.find('p', class_='text-sm')
                if company_p:
                    cert['issuer'] = company_p.get_text().strip()
                
                ql_editor = item.find('div', class_='ql-editor')
                if ql_editor:
                    p = ql_editor.find('p')
                    if p:
                        cert['description'] = p.get_text().strip()
                
                certifications.append(cert)
        
        return certifications


class CVRenderer:
    """Renders structured CV data back into HTML template."""
    
    @staticmethod
    def render(template_html: str, cv_data: Dict) -> str:
        """
        Render CV data into HTML template.
        
        Args:
            template_html: Base HTML template
            cv_data: Structured CV data dict
        
        Returns:
            Rendered HTML
        """
        soup = BeautifulSoup(template_html, 'html.parser')
        
        # Render profile
        CVRenderer._render_profile(soup, cv_data.get('profile', {}))
        
        # Render contact
        CVRenderer._render_contact(soup, cv_data.get('contact', {}))
        
        # Render links
        CVRenderer._render_links(soup, cv_data.get('links', []))
        
        # Render skills
        CVRenderer._render_skills(soup, cv_data.get('skills', []))
        
        # Render languages
        CVRenderer._render_languages(soup, cv_data.get('languages', []))
        
        # Render summary
        CVRenderer._render_summary(soup, cv_data.get('summary', ''))
        
        # Render experience
        CVRenderer._render_experience(soup, cv_data.get('experience', []))
        
        # Render education
        CVRenderer._render_education(soup, cv_data.get('education', []))
        
        # Render projects
        CVRenderer._render_projects(soup, cv_data.get('projects', []))
        
        # Render certifications
        CVRenderer._render_certifications(soup, cv_data.get('certifications', []))
        
        return str(soup)
    
    @staticmethod
    def _render_profile(soup: BeautifulSoup, profile: Dict):
        """Render profile information."""
        h1 = soup.find('h1')
        if h1 and 'name' in profile:
            h1.string = profile['name']
        
        title_p = soup.find('p', style=lambda x: x and 'font-size:1.25rem' in x)
        if title_p and 'title' in profile:
            title_p.string = profile['title']
    
    @staticmethod
    def _render_contact(soup: BeautifulSoup, contact: Dict):
        """Render contact information."""
        contact_items = soup.find_all('div', class_='contact-item')
        for item in contact_items:
            text = item.get_text().strip()
            icon = item.find('svg')
            
            if icon:
                if 'phone' in str(icon) or '+46' in text:
                    if 'phone' in contact:
                        # Replace text content
                        span = item.find('span', class_=lambda x: x != 'contact-icon')
                        if span:
                            span.string = contact['phone']
                elif 'mail' in str(icon) or '@' in text:
                    if 'email' in contact:
                        span = item.find('span', class_=lambda x: x != 'contact-icon')
                        if span:
                            span.string = contact['email']
                elif 'house' in str(icon) or 'Gothenburg' in text or 'Stockholm' in text:
                    if 'location' in contact:
                        span = item.find('span', class_=lambda x: x != 'contact-icon')
                        if span:
                            span.string = contact['location']
    
    @staticmethod
    def _render_links(soup: BeautifulSoup, links: List[Dict]):
        """Render links."""
        # Find links section
        links_section = None
        for item in soup.find_all('div', class_='contact-item'):
            a_tag = item.find('a')
            if a_tag:
                links_section = item.find_parent('div', class_='space-y-2')
                break
        
        if links_section and links:
            # Clear existing links
            existing_links = links_section.find_all('div', class_='contact-item')
            for link_item in existing_links[1:]:  # Keep first one as template
                link_item.decompose()
            
            # Add new links
            first_link = existing_links[0] if existing_links else None
            for link_data in links:
                if first_link:
                    a_tag = first_link.find('a')
                    if a_tag:
                        a_tag.string = link_data.get('text', '')
                        a_tag['href'] = link_data.get('url', '')
                    first_link = None
                else:
                    # Clone first link structure
                    new_link = soup.new_tag('div', class_='contact-item')
                    icon_span = soup.new_tag('span', class_='contact-icon')
                    svg = soup.new_tag('svg', **{
                        'class': 'lucide lucide-globe',
                        'fill': 'none',
                        'height': '16',
                        'stroke': 'currentColor',
                        'stroke-linecap': 'round',
                        'stroke-linejoin': 'round',
                        'stroke-width': '2',
                        'viewBox': '0 0 24 24',
                        'width': '16',
                        'xmlns': 'http://www.w3.org/2000/svg'
                    })
                    icon_span.append(svg)
                    a_tag = soup.new_tag('a', href=link_data.get('url', ''), target='_blank', rel='noopener noreferrer')
                    a_tag.string = link_data.get('text', '')
                    new_link.append(icon_span)
                    new_link.append(a_tag)
                    links_section.append(new_link)
    
    @staticmethod
    def _render_skills(soup: BeautifulSoup, skills: List[Dict]):
        """Render skills."""
        skill_groups = soup.find_all('div', class_='skill-group')
        
        for i, skill_group_data in enumerate(skills):
            if i < len(skill_groups):
                group = skill_groups[i]
                
                # Update category title
                title_elem = group.find('div', class_='skill-group-title')
                if title_elem:
                    title_elem.string = skill_group_data.get('category', '')
                
                # Update skill tags
                skill_tags_div = group.find('div', class_='skill-tags')
                if skill_tags_div:
                    # Clear existing tags
                    skill_tags_div.clear()
                    
                    # Add new tags
                    for skill in skill_group_data.get('items', []):
                        tag = soup.new_tag('span', class_='skill-tag')
                        tag.string = skill
                        skill_tags_div.append(tag)
    
    @staticmethod
    def _render_languages(soup: BeautifulSoup, languages: List[Dict]):
        """Render languages."""
        # Find languages section
        languages_section = None
        for h2 in soup.find_all('h2'):
            if h2.get_text().strip() == 'Languages':
                languages_section = h2.find_parent('div', class_='space-y-3')
                break
        
        if languages_section:
            lang_items = languages_section.find_all('div', class_='space-y-1')
            
            # Clear existing languages
            for item in lang_items:
                item.decompose()
            
            # Find the container div for languages (space-y-3 inside languages_section)
            container = languages_section.find('div', class_='space-y-3')
            if not container:
                container = languages_section
            
            # Add new languages
            for lang_data in languages:
                lang_item = soup.new_tag('div', class_='space-y-1')
                
                # Language name
                name_div = soup.new_tag('div', class_='flex justify-between items-center gap-4')
                name_span = soup.new_tag('span', class_='text-sm flex-1 min-w-0', style='color:#334155')
                name_span.string = lang_data.get('name', '')
                name_div.append(name_span)
                lang_item.append(name_div)
                
                # Proficiency bar
                bar_div = soup.new_tag('div', class_='language-bar')
                bar_fill = soup.new_tag('div', class_='language-bar-fill', style=f"width:{lang_data.get('proficiency', 100)}%")
                bar_div.append(bar_fill)
                lang_item.append(bar_div)
                
                container.append(lang_item)
    
    @staticmethod
    def _render_summary(soup: BeautifulSoup, summary: str):
        """Render professional summary."""
        # Find summary section
        summary_section = None
        for h2 in soup.find_all('h2'):
            if h2.get_text().strip() == 'Professional Summary':
                parent = h2.find_parent('div', class_='space-y-3')
                if parent:
                    summary_section = parent.find('div', class_='ql-editor')
                    break
        
        if summary_section and summary:
            # Clear existing content
            summary_section.clear()
            
            # Split summary into paragraphs (by double newline)
            paragraphs = summary.split('\n\n')
            for para_text in paragraphs:
                if para_text.strip():
                    p = soup.new_tag('p')
                    # Handle bold text
                    if para_text.startswith('**') and para_text.endswith('**'):
                        strong = soup.new_tag('strong')
                        strong.string = para_text[2:-2]
                        p.append(strong)
                    elif '**' in para_text:
                        # Simple bold handling
                        parts = para_text.split('**')
                        for i, part in enumerate(parts):
                            if i % 2 == 1:
                                strong = soup.new_tag('strong')
                                strong.string = part
                                p.append(strong)
                            else:
                                p.append(part)
                    else:
                        p.string = para_text.strip()
                    summary_section.append(p)
    
    @staticmethod
    def _render_experience(soup: BeautifulSoup, experience: List[Dict]):
        """Render work experience."""
        # Find experience section
        experience_section = None
        for h2 in soup.find_all('h2'):
            if h2.get_text().strip() == 'Work Experience':
                experience_section = h2.find_parent('div', class_='space-y-3')
                break
        
        if experience_section:
            timeline_items = experience_section.find_all('div', class_='timeline-item')
            
            # Clear existing experience items
            for item in timeline_items:
                item.decompose()
            
            # Add new experience items
            for exp_data in experience:
                item = soup.new_tag('div', class_='timeline-item')
                
                # Timeline dot
                dot = soup.new_tag('div', class_='timeline-dot')
                item.append(dot)
                
                # Title and date
                title_div = soup.new_tag('div', class_='flex justify-between items-baseline gap-4')
                h3 = soup.new_tag('h3', class_='flex-1 min-w-0')
                h3.string = exp_data.get('title', '')
                date_badge = soup.new_tag('span', class_='date-badge')
                date_badge.string = exp_data.get('date', '')
                title_div.append(h3)
                title_div.append(date_badge)
                item.append(title_div)
                
                # Company and location
                company_div = soup.new_tag('div', class_='flex justify-between items-baseline')
                company_p = soup.new_tag('p', class_='text-sm flex-1 min-w-0')
                company_p.string = exp_data.get('company', '')
                location_p = soup.new_tag('p', class_='flex-shrink-0 text-xs')
                location_p.string = exp_data.get('location', '')
                company_div.append(company_p)
                company_div.append(location_p)
                item.append(company_div)
                
                # Description
                ql_editor = soup.new_tag('div', class_='ql-editor break-words text-sm leading-tight')
                
                # Add description paragraphs
                for desc in exp_data.get('description', []):
                    p = soup.new_tag('p')
                    p.string = desc
                    ql_editor.append(p)
                
                # Add bullets
                if exp_data.get('bullets'):
                    ol = soup.new_tag('ol')
                    for bullet_text in exp_data.get('bullets', []):
                        li = soup.new_tag('li', attrs={'data-list': 'bullet'})
                        span = soup.new_tag('span', class_='ql-ui', contenteditable='false')
                        li.append(span)
                        # Handle bold text in bullets
                        if '**' in bullet_text:
                            parts = bullet_text.split('**')
                            for i, part in enumerate(parts):
                                if i % 2 == 1:
                                    strong = soup.new_tag('strong')
                                    strong.string = part
                                    li.append(strong)
                                else:
                                    li.append(part)
                        else:
                            li.append(bullet_text)
                        ol.append(li)
                    ql_editor.append(ol)
                
                # Add technologies
                if exp_data.get('technologies'):
                    p = soup.new_tag('p')
                    strong = soup.new_tag('strong')
                    strong.string = 'Key Technologies: '
                    p.append(strong)
                    p.append(exp_data.get('technologies', ''))
                    ql_editor.append(p)
                
                item.append(ql_editor)
                # Find the container div for experience items
                container = experience_section.find('div', class_='space-y-3')
                if not container:
                    container = experience_section
                container.append(item)
    
    @staticmethod
    def _render_education(soup: BeautifulSoup, education: List[Dict]):
        """Render education."""
        # Find education section
        education_section = None
        for h2 in soup.find_all('h2'):
            if h2.get_text().strip() == 'Education':
                education_section = h2.find_parent('div', class_='space-y-3')
                break
        
        if education_section:
            timeline_items = education_section.find_all('div', class_='timeline-item')
            
            # Clear existing education items
            for item in timeline_items:
                item.decompose()
            
            # Add new education items
            for edu_data in education:
                item = soup.new_tag('div', class_='timeline-item')
                
                dot = soup.new_tag('div', class_='timeline-dot')
                item.append(dot)
                
                title_div = soup.new_tag('div', class_='flex justify-between items-baseline gap-4')
                h3 = soup.new_tag('h3', class_='flex-1 min-w-0')
                h3.string = edu_data.get('degree', '')
                date_badge = soup.new_tag('span', class_='date-badge')
                date_badge.string = edu_data.get('date', '')
                title_div.append(h3)
                title_div.append(date_badge)
                item.append(title_div)
                
                company_div = soup.new_tag('div', class_='flex justify-between items-baseline')
                company_p = soup.new_tag('p', class_='text-sm flex-1 min-w-0')
                company_p.string = edu_data.get('institution', '')
                location_p = soup.new_tag('p', class_='flex-shrink-0 text-xs')
                location_p.string = edu_data.get('location', '')
                company_div.append(company_p)
                company_div.append(location_p)
                item.append(company_div)
                
                if edu_data.get('description'):
                    ql_editor = soup.new_tag('div', class_='ql-editor break-words text-sm leading-tight')
                    p = soup.new_tag('p')
                    p.string = edu_data.get('description', '')
                    ql_editor.append(p)
                    item.append(ql_editor)
                
                # Find the container div for education items
                container = education_section.find('div', class_='space-y-3')
                if not container:
                    container = education_section
                container.append(item)
    
    @staticmethod
    def _render_projects(soup: BeautifulSoup, projects: List[Dict]):
        """Render projects."""
        # Find projects section
        projects_section = None
        for h2 in soup.find_all('h2'):
            if h2.get_text().strip() == 'Projects':
                projects_section = h2.find_parent('div', class_='space-y-3')
                break
        
        if projects_section:
            timeline_items = projects_section.find_all('div', class_='timeline-item')
            
            # Clear existing projects
            for item in timeline_items:
                item.decompose()
            
            # Add new projects
            for proj_data in projects:
                item = soup.new_tag('div', class_='timeline-item')
                
                dot = soup.new_tag('div', class_='timeline-dot')
                item.append(dot)
                
                title_div = soup.new_tag('div', class_='flex justify-between items-baseline gap-4')
                h3 = soup.new_tag('h3', class_='flex-1 min-w-0')
                if proj_data.get('url'):
                    a = soup.new_tag('a', href=proj_data.get('url', ''), target='_blank', rel='noopener noreferrer')
                    a.string = proj_data.get('title', '')
                    h3.append(a)
                else:
                    h3.string = proj_data.get('title', '')
                date_badge = soup.new_tag('span', class_='date-badge')
                date_badge.string = proj_data.get('date', '')
                title_div.append(h3)
                title_div.append(date_badge)
                item.append(title_div)
                
                ql_editor = soup.new_tag('div', class_='ql-editor break-words text-sm leading-tight')
                
                if proj_data.get('description'):
                    p = soup.new_tag('p')
                    p.string = proj_data.get('description', '')
                    ql_editor.append(p)
                
                if proj_data.get('bullets'):
                    ol = soup.new_tag('ol')
                    for bullet_text in proj_data.get('bullets', []):
                        li = soup.new_tag('li', attrs={'data-list': 'bullet'})
                        span = soup.new_tag('span', class_='ql-ui', contenteditable='false')
                        li.append(span)
                        if '**' in bullet_text:
                            parts = bullet_text.split('**')
                            for i, part in enumerate(parts):
                                if i % 2 == 1:
                                    strong = soup.new_tag('strong')
                                    strong.string = part
                                    li.append(strong)
                                else:
                                    li.append(part)
                        else:
                            li.append(bullet_text)
                        ol.append(li)
                    ql_editor.append(ol)
                
                if proj_data.get('technologies'):
                    p = soup.new_tag('p')
                    strong = soup.new_tag('strong')
                    strong.string = 'Key Technologies: '
                    p.append(strong)
                    p.append(proj_data.get('technologies', ''))
                    ql_editor.append(p)
                
                item.append(ql_editor)
                # Find the container div for projects
                container = projects_section.find('div', class_='space-y-3')
                if not container:
                    container = projects_section
                container.append(item)
    
    @staticmethod
    def _render_certifications(soup: BeautifulSoup, certifications: List[Dict]):
        """Render certifications."""
        # Find certifications section
        cert_section = None
        for h2 in soup.find_all('h2'):
            if h2.get_text().strip() == 'Certifications':
                cert_section = h2.find_parent('div', class_='space-y-3')
                break
        
        if cert_section:
            timeline_items = cert_section.find_all('div', class_='timeline-item')
            
            # Clear existing certifications
            for item in timeline_items:
                item.decompose()
            
            # Add new certifications
            for cert_data in certifications:
                item = soup.new_tag('div', class_='timeline-item')
                
                dot = soup.new_tag('div', class_='timeline-dot')
                item.append(dot)
                
                title_div = soup.new_tag('div', class_='flex justify-between items-baseline gap-4')
                h3 = soup.new_tag('h3', class_='flex-1 min-w-0')
                if cert_data.get('url'):
                    a = soup.new_tag('a', href=cert_data.get('url', ''), target='_blank', rel='noopener noreferrer')
                    a.string = cert_data.get('title', '')
                    h3.append(a)
                else:
                    h3.string = cert_data.get('title', '')
                date_badge = soup.new_tag('span', class_='date-badge')
                date_badge.string = cert_data.get('date', '')
                title_div.append(h3)
                title_div.append(date_badge)
                item.append(title_div)
                
                if cert_data.get('issuer'):
                    company_div = soup.new_tag('div', class_='flex justify-between items-baseline')
                    company_p = soup.new_tag('p', class_='text-sm flex-1 min-w-0')
                    company_p.string = cert_data.get('issuer', '')
                    company_div.append(company_p)
                    item.append(company_div)
                
                if cert_data.get('description'):
                    ql_editor = soup.new_tag('div', class_='ql-editor break-words text-sm leading-tight')
                    p = soup.new_tag('p')
                    p.string = cert_data.get('description', '')
                    ql_editor.append(p)
                    item.append(ql_editor)
                
                # Find the container div for certifications
                container = cert_section.find('div', class_='space-y-3')
                if not container:
                    container = cert_section
                container.append(item)




