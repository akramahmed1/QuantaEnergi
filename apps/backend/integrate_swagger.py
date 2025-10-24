"""
Integration script to add Swagger UI to existing FastAPI app
Run this script to integrate Swagger UI with your QuantaEnergi API
"""

import os
import sys
from pathlib import Path

def integrate_swagger_ui():
    """
    Integrate Swagger UI with the existing FastAPI application
    """
    
    # Add the swagger setup to main.py
    main_py_path = Path("main.py")
    
    if main_py_path.exists():
        with open(main_py_path, "r") as f:
            content = f.read()
        
        # Check if swagger setup is already added
        if "setup_swagger_ui" not in content:
            # Add import and setup at the end of main.py
            swagger_import = """
# Swagger UI Integration
from swagger_ui_setup import setup_swagger_ui

# Set up Swagger UI
app = setup_swagger_ui(app)
"""
            
            # Add before the final if __name__ == "__main__" block
            if 'if __name__ == "__main__":' in content:
                content = content.replace(
                    'if __name__ == "__main__":',
                    swagger_import + '\nif __name__ == "__main__":'
                )
            else:
                content += swagger_import
            
            with open(main_py_path, "w") as f:
                f.write(content)
            
            print("✅ Swagger UI integration added to main.py")
        else:
            print("ℹ️  Swagger UI already integrated in main.py")
    else:
        print("❌ main.py not found. Please run this script from the backend directory.")
        return False
    
    # Create a simple test script
    test_script = '''#!/usr/bin/env python3
"""
Test script to verify Swagger UI integration
"""

import requests
import json

def test_swagger_endpoints():
    """Test Swagger UI endpoints"""
    base_url = "http://localhost:8000"
    
    endpoints = [
        "/docs",
        "/redoc", 
        "/openapi.json",
        "/openapi.yaml"
    ]
    
    print("🧪 Testing Swagger UI endpoints...")
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}")
            if response.status_code == 200:
                print(f"✅ {endpoint} - OK")
            else:
                print(f"❌ {endpoint} - Status: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"❌ {endpoint} - Connection failed (server not running?)")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")

if __name__ == "__main__":
    test_swagger_endpoints()
'''
    
    with open("test_swagger.py", "w") as f:
        f.write(test_script)
    
    print("✅ Test script created: test_swagger.py")
    print("\n📋 Next steps:")
    print("1. Start your FastAPI server: python main.py")
    print("2. Open http://localhost:8000/docs for Swagger UI")
    print("3. Open http://localhost:8000/redoc for ReDoc")
    print("4. Run python test_swagger.py to test endpoints")
    
    return True

if __name__ == "__main__":
    integrate_swagger_ui()
