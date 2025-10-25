"""
Simple Desktop Launcher for HealthCareKit
This script launches the Streamlit app and opens it in the default browser.
"""

import subprocess
import time
import sys
import webbrowser
import requests


def start_streamlit_process():
    """Start the Streamlit server as a subprocess"""
    try:
        # Start Streamlit as a subprocess
        process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", "app.py", 
            "--server.headless", "true", "--server.port", "8501"
        ])
        return process
    except Exception as e:
        print(f"Error starting Streamlit: {e}")
        return None


def wait_for_server(url, timeout=30):
    """Wait for the Streamlit server to be ready"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=1)
            if response.status_code == 200:
                return True
        except:
            pass
        time.sleep(0.5)
    return False


def main():
    """Main function to launch the desktop app"""
    print("Starting HealthCareKit server...")
    
    # Start Streamlit as a subprocess
    streamlit_process = start_streamlit_process()
    if not streamlit_process:
        print("Streamlit process started successfully!")
    else:
        print("ERROR: Failed to start Streamlit process")
        sys.exit(1)
    
    # Wait for the server to start
    url = "http://localhost:8501"
    
    if wait_for_server(url):
        print("Server ready! Opening in browser...")
        webbrowser.open(url)
        print("HealthCareKit is now running in your browser!")
        print("Press Ctrl+C to stop the server.")
        
        try:
            # Keep the process running
            streamlit_process.wait()
        except KeyboardInterrupt:
            print("\nShutting down HealthCareKit...")
            streamlit_process.terminate()
            streamlit_process.wait()
            print("Goodbye!")
    else:
        print("ERROR: Failed to start Streamlit server within timeout period")
        if streamlit_process.poll() is None:
            streamlit_process.terminate()
        sys.exit(1)


if __name__ == '__main__':
    main()
