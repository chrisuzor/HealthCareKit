"""
Quick Test Script for Desktop App Components
Run this to verify everything is installed correctly before building.
"""

import sys

def check_module(module_name, package_name=None):
    """Check if a module is installed"""
    if package_name is None:
        package_name = module_name
    
    try:
        __import__(module_name)
        print(f"✓ {package_name} is installed")
        return True
    except ImportError:
        print(f"✗ {package_name} is NOT installed - run: pip install {package_name}")
        return False


def main():
    """Check all required dependencies"""
    print("=" * 60)
    print("HealthCareKit Desktop App - Dependency Check")
    print("=" * 60)
    print()
    
    modules = [
        ('streamlit', 'streamlit'),
        ('webview', 'pywebview'),
        ('requests', 'requests'),
        ('pandas', 'pandas'),
        ('numpy', 'numpy'),
        ('plotly', 'plotly'),
        ('PyInstaller', 'pyinstaller'),
    ]
    
    all_installed = True
    for module, package in modules:
        if not check_module(module, package):
            all_installed = False
    
    print()
    print("=" * 60)
    if all_installed:
        print("SUCCESS! All dependencies are installed.")
        print("You can now run: python build_desktop_app.py")
    else:
        print("MISSING DEPENDENCIES!")
        print("Install them with: pip install -r requirements.txt")
        print("Then install: pip install pyinstaller")
    print("=" * 60)


if __name__ == '__main__':
    main()
