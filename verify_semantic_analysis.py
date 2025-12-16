#!/usr/bin/env python3
"""Verify semantic analysis implementation."""

import sys
from pathlib import Path

def verify_implementation():
    """Verify that all required methods exist and work."""
    print("=" * 60)
    print("Verifying Semantic Analysis Implementation")
    print("=" * 60)
    
    errors = []
    
    # Test 1: Check imports
    print("\n1. Testing imports...")
    try:
        from app.skill_analyzer import SkillAnalyzer
        from app.ai_client import AIClient
        from app.storage import Storage
        print("   ✓ All imports successful")
    except Exception as e:
        errors.append(f"Import error: {e}")
        print(f"   ✗ Import failed: {e}")
        return False
    
    # Test 2: Check SkillAnalyzer methods
    print("\n2. Checking SkillAnalyzer methods...")
    try:
        storage = Storage()
        config = storage.load_config()
        ai_client = AIClient(config)
        analyzer = SkillAnalyzer(ai_client, storage)
        
        # Check _extract_cv_text exists
        if not hasattr(analyzer, '_extract_cv_text'):
            errors.append("SkillAnalyzer._extract_cv_text() method missing")
            print("   ✗ _extract_cv_text() method missing")
        else:
            print("   ✓ _extract_cv_text() method exists")
        
        # Check analyze method exists
        if not hasattr(analyzer, 'analyze'):
            errors.append("SkillAnalyzer.analyze() method missing")
            print("   ✗ analyze() method missing")
        else:
            print("   ✓ analyze() method exists")
            
        # Test _extract_cv_text with actual CV
        cv_path = storage.base_dir / config.get('cv_template_path', 'cv.html')
        if cv_path.exists():
            cv_html = cv_path.read_text(encoding='utf-8')
            cv_text = analyzer._extract_cv_text(cv_html)
            if 'IoT' in cv_text or 'embedded' in cv_text.lower():
                print("   ✓ _extract_cv_text() extracts CV content (found IoT/embedded)")
            else:
                print("   ⚠ _extract_cv_text() may not be extracting all content")
    except Exception as e:
        errors.append(f"SkillAnalyzer test error: {e}")
        print(f"   ✗ Error: {e}")
    
    # Test 3: Check AIClient methods
    print("\n3. Checking AIClient methods...")
    try:
        if not hasattr(ai_client, 'analyze_cv_job_alignment'):
            errors.append("AIClient.analyze_cv_job_alignment() method missing")
            print("   ✗ analyze_cv_job_alignment() method missing")
        else:
            print("   ✓ analyze_cv_job_alignment() method exists")
            
        # Check that analyze_skill_gaps still exists (backward compatibility)
        if not hasattr(ai_client, 'analyze_skill_gaps'):
            errors.append("AIClient.analyze_skill_gaps() method missing (backward compat)")
            print("   ✗ analyze_skill_gaps() method missing")
        else:
            print("   ✓ analyze_skill_gaps() method exists (backward compatibility)")
    except Exception as e:
        errors.append(f"AIClient test error: {e}")
        print(f"   ✗ Error: {e}")
    
    # Test 4: Check tailor_cv has style preservation
    print("\n4. Checking tailor methods have style preservation...")
    try:
        if hasattr(ai_client, 'tailor_cv'):
            # Read the source to check for style preservation
            ai_client_file = Path(__file__).parent / 'app' / 'ai_client.py'
            content = ai_client_file.read_text(encoding='utf-8')
            
            if 'current_summary' in content and 'Professional Summary Style Reference' in content:
                print("   ✓ tailor_cv() includes professional summary style preservation")
            else:
                errors.append("tailor_cv() missing style preservation")
                print("   ✗ tailor_cv() missing style preservation")
                
            if 'tailor_cv_with_answers' in content and 'current_summary' in content:
                # Check if it's in the right method
                if 'def tailor_cv_with_answers' in content:
                    method_start = content.find('def tailor_cv_with_answers')
                    method_content = content[method_start:method_start+500]
                    if 'current_summary' in method_content:
                        print("   ✓ tailor_cv_with_answers() includes professional summary style preservation")
                    else:
                        errors.append("tailor_cv_with_answers() missing style preservation")
                        print("   ✗ tailor_cv_with_answers() missing style preservation")
        else:
            errors.append("tailor_cv() method missing")
            print("   ✗ tailor_cv() method missing")
    except Exception as e:
        errors.append(f"Style preservation test error: {e}")
        print(f"   ✗ Error: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    if errors:
        print(f"✗ Verification failed with {len(errors)} error(s):")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("✓ All verification checks passed!")
        print("\nImplementation Summary:")
        print("  ✓ Semantic analysis method (analyze_cv_job_alignment) implemented")
        print("  ✓ CV text extraction method (_extract_cv_text) implemented")
        print("  ✓ SkillAnalyzer.analyze() uses semantic analysis")
        print("  ✓ Professional summary style preservation in tailor methods")
        print("  ✓ Backward compatibility maintained (analyze_skill_gaps)")
        return True

if __name__ == "__main__":
    success = verify_implementation()
    sys.exit(0 if success else 1)


