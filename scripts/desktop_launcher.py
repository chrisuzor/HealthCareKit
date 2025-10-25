"""
Desktop Launcher for HealthCareKit
This script launches the Streamlit app in a native desktop window using PyWebView.
"""

import webview
import threading
import time
import sys
import os
from streamlit.web import cli as stcli


def start_streamlit():
    """Start the Streamlit server in a background thread"""
    sys.argv = ["streamlit", "run", "app.py", "--server.headless", "true", "--server.port", "8501"]
    stcli.main()


def wait_for_server(url, timeout=30):
    """Wait for the Streamlit server to be ready"""
    import requests
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
    # Start Streamlit in a background thread
    streamlit_thread = threading.Thread(target=start_streamlit, daemon=True)
    streamlit_thread.start()
    
    # Wait for the server to start
    print("Starting HealthCareKit server...")
    url = "http://localhost:8501"
    
    if wait_for_server(url):
        print("Server ready! Opening desktop window...")
        # Create and start the desktop window
        window = webview.create_window(
            'HealthCareKit - AI-Powered Vital Monitoring',
            url,
            width=1400,
            height=900,
            resizable=True,
            fullscreen=False
        )
        webview.start()
    else:
        print("ERROR: Failed to start Streamlit server within timeout period")
        sys.exit(1)


if __name__ == '__main__':
    main()
