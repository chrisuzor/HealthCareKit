"""
Application Launcher for Maxio Health System
This script checks dependencies and starts the Streamlit application
"""

import sys
import subprocess
import os

def check_dependencies():
    """Check if all required Python packages are installed"""
    required_packages = [
        'streamlit',
        'requests', 
        'plotly',
        'pandas',
        'numpy',
        'serial'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f" Missing dependencies: {', '.join(missing_packages)}")
        print("Please install missing packages using: pip install -r requirements.txt")
        return False
    
    print(" All required modules are installed")
    return True

def check_app_file():
    """Check if the main application file exists"""
    if not os.path.exists("app.py"):
        print(" app.py not found. Please run this script from the HealthCareKit directory.")
        return False
    
    print("✅ Main application file found")
    return True

def start_application():
    """Start the Streamlit application"""
    try:
        print(" Launching Streamlit application...")
        print(" The application will open in your web browser")
        print(" Press Ctrl+C to stop the application")
        
        # Start Streamlit with the main app
        subprocess.run(["streamlit", "run", "app.py"], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running Streamlit application: {e}")
        return False
    except KeyboardInterrupt:
        print("\n Application stopped by user")
        return True
    except Exception as e:
        print(f" Unexpected error: {e}")
        return False

def main():
    """Main function to run the application"""
    print(" Starting Maxio Health System...")
    print("=" * 50)
    
    # Step 1: Check if all dependencies are installed
    if not check_dependencies():
        sys.exit(1)
    
    # Step 2: Check if the main app file exists
    if not check_app_file():
        sys.exit(1)
    
    # Step 3: Start the application
    success = start_application()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main() 