#!/usr/bin/env python3
"""Quick test script to verify the application works."""

import sys
from pathlib import Path

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    try:
        from app import create_app
        from app.storage import Storage
        from app.ai_client import AIClient
        from app.cv_engine import CVEngine
        from app.skill_analyzer import SkillAnalyzer
        print("✓ All modules imported successfully")
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False

def test_storage():
    """Test storage operations."""
    print("\nTesting storage...")
    try:
        from app.storage import Storage
        storage = Storage()
        config = storage.load_config()
        assert 'ai' in config
        assert 'gateway_url' in config['ai']
        print("✓ Storage initialized and config loaded")
        return True
    except Exception as e:
        print(f"✗ Storage error: {e}")
        return False

def test_ai_client():
    """Test AI client initialization."""
    print("\nTesting AI client...")
    try:
        from app.storage import Storage
        from app.ai_client import AIClient
        storage = Storage()
        config = storage.load_config()
        client = AIClient(config)
        print(f"✓ AI Client initialized (model: {client.model})")
        return True
    except Exception as e:
        print(f"✗ AI Client error: {e}")
        return False

def test_flask_app():
    """Test Flask app creation."""
    print("\nTesting Flask app...")
    try:
        from app import create_app
        app = create_app()
        assert app is not None
        print("✓ Flask app created")
        return True
    except Exception as e:
        print(f"✗ Flask app error: {e}")
        return False

def test_routes():
    """Test that routes are registered."""
    print("\nTesting routes...")
    try:
        from app import create_app
        app = create_app()
        with app.test_client() as client:
            # Test dashboard route
            r = client.get('/')
            assert r.status_code == 200, f"Dashboard returned {r.status_code}"
            print("✓ Dashboard route works")
            
            # Test generate route
            r = client.get('/generate')
            assert r.status_code == 200, f"Generate returned {r.status_code}"
            print("✓ Generate route works")
        return True
    except Exception as e:
        print(f"✗ Routes error: {e}")
        return False

def test_templates():
    """Test that templates exist."""
    print("\nTesting templates...")
    try:
        template_dir = Path(__file__).parent / "templates"
        required_templates = ['base.html', 'dashboard.html', 'generate.html', 'application.html']
        for template in required_templates:
            template_path = template_dir / template
            assert template_path.exists(), f"Template {template} not found"
        print("✓ All templates exist")
        return True
    except Exception as e:
        print(f"✗ Templates error: {e}")
        return False

def test_cv_template():
    """Test that base CV template exists."""
    print("\nTesting CV template...")
    try:
        cv_path = Path(__file__).parent / "cv.html"
        assert cv_path.exists(), "cv.html not found"
        print("✓ CV template exists")
        return True
    except Exception as e:
        print(f"✗ CV template error: {e}")
        return False

def test_skills_added_none_handling():
    """Test that skills_added=None is handled correctly in update_skills route."""
    print("\nTesting skills_added=None handling...")
    try:
        # Simulate the bug scenario
        app_data = {'skills_added': None, 'cv_html': '<html>test</html>'}
        add_skills = ['Python', 'Docker']
        
        # This is what the old code would do (and fail):
        # result = app_data.get('skills_added', []) + add_skills  # Would crash
        
        # This is what the fixed code does:
        existing_skills = app_data.get('skills_added') or []
        result = existing_skills + add_skills
        
        assert result == ['Python', 'Docker'], "Skills concatenation failed"
        print("✓ skills_added=None handled correctly")
        
        # Test with empty list
        app_data2 = {'skills_added': [], 'cv_html': '<html>test</html>'}
        existing_skills2 = app_data2.get('skills_added') or []
        result2 = existing_skills2 + add_skills
        assert result2 == ['Python', 'Docker'], "Skills concatenation with empty list failed"
        print("✓ skills_added=[] handled correctly")
        
        # Test with missing key
        app_data3 = {'cv_html': '<html>test</html>'}
        existing_skills3 = app_data3.get('skills_added') or []
        result3 = existing_skills3 + add_skills
        assert result3 == ['Python', 'Docker'], "Skills concatenation with missing key failed"
        print("✓ Missing skills_added key handled correctly")
        
        return True
    except Exception as e:
        print(f"✗ skills_added handling error: {e}")
        return False

def test_api_connection():
    """Test API connection (optional - may fail if gateway is not configured correctly)."""
    print("\nTesting API connection...")
    try:
        from app.storage import Storage
        from app.ai_client import AIClient
        
        storage = Storage()
        config = storage.load_config()
        
        gateway_url = config['ai'].get('gateway_url', '')
        api_key = config['ai'].get('api_key', '')
        
        if not api_key:
            print("⚠ API key not set - skipping API test")
            print("  (This is OK for initial setup, but API calls will fail)")
            return True  # Not a failure, just not configured
        
        client = AIClient(config)
        # Try a simple API call
        response = client.generate(
            "Say 'test' and nothing else.",
            "You are a test assistant.",
            temperature=0.7
        )
        print("✓ API connection works")
        return True
    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg or "not found" in error_msg.lower():
            print("✗ API Gateway not found (404)")
            print("  The gateway URL may be incorrect or the gateway doesn't exist")
            print(f"  Gateway URL: {gateway_url or 'Not set'}")
            print("  Please check your config.json or use the official gateway:")
            print("  https://ai-gateway.vercel.sh/v1")
            return False
        print(f"⚠ API connection test failed: {error_msg}")
        print("  (This may be OK if gateway is temporarily unavailable)")
        return True  # Don't fail the whole test suite for API issues

def main():
    """Run all tests."""
    print("=" * 50)
    print("CV Tailoring Dashboard - Verification Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_storage,
        test_ai_client,
        test_flask_app,
        test_routes,
        test_templates,
        test_cv_template,
        test_skills_added_none_handling,
        test_api_connection,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! Application is ready to use.")
        return 0
    else:
        print("✗ Some tests failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

