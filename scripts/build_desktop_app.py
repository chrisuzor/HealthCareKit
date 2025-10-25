"""
Build Script for HealthCareKit Desktop App
This script automates the PyInstaller build process for the desktop application.
"""

import os
import subprocess
import sys
import shutil


def clean_build():
    """Clean previous build artifacts"""
    print("Cleaning previous build artifacts...")
    # Build artifacts are in parent directory
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dirs_to_remove = ['build', 'dist']
    for dir_name in dirs_to_remove:
        dir_path = os.path.join(parent_dir, dir_name)
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
            print(f"  - Removed {dir_name}/")


def run_pyinstaller():
    """Run PyInstaller with the correct parameters"""
    print("\nBuilding desktop application with PyInstaller...")
    
    command = [
        'pyinstaller',
        '--onefile',
        '--windowed',  # No console window
        '--name', 'HealthCareKit',
        '--hidden-import', 'streamlit',
        '--hidden-import', 'streamlit.web.cli',
        '--hidden-import', 'pandas',
        '--hidden-import', 'numpy',
        '--hidden-import', 'plotly',
        '--hidden-import', 'requests',
        '--hidden-import', 'webview',
        '--hidden-import', 'pythonnet',
        '--hidden-import', 'core.vital_monitor',
        '--hidden-import', 'core.ai_assistant',
        '--hidden-import', 'core.esp32_interface',
        '--hidden-import', 'core.health_analytics',
        '--hidden-import', 'core.emergency_alerts',
        '--hidden-import', 'core.patient_profile',
        '--hidden-import', 'core.health_goals',
        '--hidden-import', 'core.notifications',
        '--hidden-import', 'utils.ui_helpers',
        '--add-data', '../core;core',
        '--add-data', '../utils;utils',
        '--add-data', '../config.py;.',
        '--add-data', '../app.py;.',
        '--collect-all', 'streamlit',
        '--collect-all', 'altair',
        'desktop_launcher.py'
    ]
    
    result = subprocess.run(command)
    return result.returncode == 0


def main():
    """Main build process"""
    print("=" * 60)
    print("HealthCareKit Desktop App Build Script")
    print("=" * 60)
    
    # Change to project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(os.path.join(project_root, 'scripts'))
    
    # Step 1: Clean previous builds
    clean_build()
    
    # Step 2: Run PyInstaller
    if run_pyinstaller():
        print("=" * 60)
        print("BUILD SUCCESSFUL!")
        print("=" * 60)
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        print(f"\nYour desktop app is ready at: {os.path.join(parent_dir, 'dist', 'HealthCareKit.exe')}")
        print("\nTo test it:")
        print("  1. Navigate to the dist/ folder")
        print("  2. Double-click HealthCareKit.exe")
        print("  3. A window should open with your app running")
    else:
        print("\n" + "=" * 60)
        print("BUILD FAILED!")
        print("=" * 60)
        print("\nPlease check the error messages above.")
        print("Common issues:")
        print("  - PyInstaller not installed: pip install pyinstaller")
        print("  - Missing dependencies: pip install -r requirements.txt")
        sys.exit(1)


if __name__ == '__main__':
    main()
