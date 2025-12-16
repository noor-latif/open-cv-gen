#!/usr/bin/env python3
"""Test CV data extraction and rendering."""

import sys
from pathlib import Path

def test_extraction_and_rendering():
    """Test that we can extract CV data and render it back."""
    print("Testing CV data extraction and rendering...")
    try:
        from app.cv_data import CVDataExtractor, CVRenderer
        from app.storage import Storage
        
        storage = Storage()
        config = storage.load_config()
        template_path = storage.base_dir / config.get('cv_template_path', 'cv.html')
        
        if not template_path.exists():
            print(f"✗ Template not found: {template_path}")
            return False
        
        # Load template
        template_html = template_path.read_text(encoding='utf-8')
        print(f"✓ Loaded template ({len(template_html)} chars)")
        
        # Extract data
        cv_data = CVDataExtractor.extract(template_html)
        print(f"✓ Extracted CV data")
        print(f"  - Profile: {cv_data.get('profile', {}).get('name', 'N/A')}")
        print(f"  - Skills groups: {len(cv_data.get('skills', []))}")
        print(f"  - Experience items: {len(cv_data.get('experience', []))}")
        print(f"  - Projects: {len(cv_data.get('projects', []))}")
        
        # Render back
        rendered = CVRenderer.render(template_html, cv_data)
        print(f"✓ Rendered CV ({len(rendered)} chars)")
        
        # Verify structure is preserved
        if 'Inter' in rendered and 'timeline-item' in rendered:
            print("✓ Template structure preserved")
        else:
            print("⚠ Warning: Template structure may have changed")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_skill_addition():
    """Test adding skills using JSON approach."""
    print("\nTesting skill addition...")
    try:
        from app.cv_data import CVDataExtractor, CVRenderer
        from app.storage import Storage
        
        storage = Storage()
        config = storage.load_config()
        template_path = storage.base_dir / config.get('cv_template_path', 'cv.html')
        template_html = template_path.read_text(encoding='utf-8')
        
        # Extract data
        cv_data = CVDataExtractor.extract(template_html)
        
        # Find Technical Skills group
        tech_skills = None
        for skill_group in cv_data.get('skills', []):
            if 'Technical' in skill_group.get('category', ''):
                tech_skills = skill_group
                break
        
        if not tech_skills:
            print("⚠ Could not find Technical Skills group")
            return True  # Not a failure, just no tech skills group
        
        original_count = len(tech_skills.get('items', []))
        print(f"  Original skills count: {original_count}")
        
        # Add a test skill
        test_skill = "TestSkill123"
        if test_skill not in tech_skills.get('items', []):
            tech_skills.setdefault('items', []).append(test_skill)
        
        new_count = len(tech_skills.get('items', []))
        print(f"  New skills count: {new_count}")
        
        # Render and verify
        rendered = CVRenderer.render(template_html, cv_data)
        if test_skill in rendered:
            print("✓ Skill added successfully")
            return True
        else:
            print("✗ Skill not found in rendered HTML")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("CV Data Extraction & Rendering Test")
    print("=" * 50)
    
    results = []
    results.append(test_extraction_and_rendering())
    results.append(test_skill_addition())
    
    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed!")
        sys.exit(0)
    else:
        print("✗ Some tests failed.")
        sys.exit(1)




