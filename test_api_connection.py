#!/usr/bin/env python3
"""Test API connection to verify gateway is working."""

import sys
from app.storage import Storage
from app.ai_client import AIClient

def test_api_connection():
    """Test that the API connection works."""
    print("Testing API Connection...")
    print("=" * 50)
    
    try:
        storage = Storage()
        config = storage.load_config()
        
        gateway_url = config['ai'].get('gateway_url', '')
        model = config['ai'].get('model', 'gpt-4')
        has_key = bool(config['ai'].get('api_key', ''))
        
        print(f"Gateway URL: {gateway_url or 'None (using OpenAI directly)'}")
        print(f"Model: {model}")
        print(f"API Key: {'Set' if has_key else 'NOT SET'}")
        print()
        
        if not has_key:
            print("❌ API key not set. Please configure in config.json or set VERCEL_AI_API_KEY")
            return False
        
        print("Initializing AI client...")
        client = AIClient(config)
        print(f"✓ Client initialized")
        print(f"  Base URL: {client.client.base_url}")
        print()
        
        print("Testing API call with simple prompt...")
        response = client.generate(
            "Say 'Hello, API is working!' and nothing else.",
            "You are a test assistant.",
            temperature=0.7
        )
        
        print(f"✓ API call successful!")
        print(f"  Response: {response[:100]}")
        print()
        print("=" * 50)
        print("✓ API connection test PASSED")
        return True
        
    except Exception as e:
        print(f"❌ API connection test FAILED")
        print(f"Error: {str(e)}")
        print()
        print("Troubleshooting:")
        print("1. Check that your gateway URL is correct")
        print("   - Official Vercel Gateway: https://ai-gateway.vercel.sh/v1")
        print("   - Custom gateway should end with /v1")
        print("2. Verify your API key is valid")
        print("3. Check that the gateway is accessible")
        print("4. If using a custom gateway, ensure it's running and accessible")
        return False

if __name__ == "__main__":
    success = test_api_connection()
    sys.exit(0 if success else 1)


