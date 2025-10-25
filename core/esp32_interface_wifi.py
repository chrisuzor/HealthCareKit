"""
WiFi path to your ESP32. We hit an API, grab vitals, and keep it moving.
Serial not your vibe? This is the wireless route.
"""

import requests
import time
import threading
from datetime import datetime
import streamlit as st

class ESP32InterfaceWiFi:
    def __init__(self, api_url="http://localhost:5000"):
        """
        Point us at your API base URL and we’ll do the rest.
        Args:
            api_url (str): where your server lives
        """
        self.api_url = api_url
        self.is_connected = False
        
        # Store current vital data
        self.vital_data = self._initialize_vital_data()
        
        # Threading variables for continuous monitoring
        self.data_thread = None
        self.stop_thread = False
        
    def _initialize_vital_data(self):
        """Default vitals so UI has something to show even before data."""
        return {
            'heart_rate': 0,
            'blood_pressure_systolic': 0,
            'blood_pressure_diastolic': 0,
            'temperature': 0,
            'oxygen_saturation': 0,
            'respiratory_rate': 0,
            'timestamp': None
        }
    
    def check_connection(self):
        """Ping the status endpoint. Green light or not?"""
        try:
            response = requests.get(f"{self.api_url}/api/status", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def connect(self):
        """Try a status call and mark us connected if it smiles back."""
        try:
            # Test connection to API
            response = requests.get(f"{self.api_url}/api/status", timeout=5)
            
            if response.status_code == 200:
                self.is_connected = True
                status_data = response.json()
                device_id = status_data.get('device_id', 'Unknown')
                st.success(f"✅ Connected to API Server - Device: {device_id}")
                return True
            else:
                st.error(f"❌ API server returned status {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            st.error(f"❌ Cannot connect to API server at {self.api_url}")
            st.info("💡 Make sure the API server is running: python api_server.py")
            return False
        except Exception as e:
            st.error(f"❌ Connection error: {str(e)}")
            return False
    
    def disconnect(self):
        """Stop the loop and mark disconnected. Clean exit."""
        self.stop_thread = True
        self.is_connected = False
        st.info("🔌 Disconnected from API server")
    
    def get_latest_vitals(self):
        """GET /api/vitals/latest and map to our fields. Straightforward."""
        if not self.is_connected:
            return None
        
        try:
            response = requests.get(f"{self.api_url}/api/vitals/latest", timeout=2)
            
            if response.status_code == 200:
                data = response.json()
                
                if data['status'] == 'success':
                    vital_info = data['data']
                    
                    # Convert to our format
                    self.vital_data = {
                        'heart_rate': vital_info.get('heart_rate', 0),
                        'blood_pressure_systolic': vital_info.get('blood_pressure_systolic', 0),
                        'blood_pressure_diastolic': vital_info.get('blood_pressure_diastolic', 0),
                        'temperature': vital_info.get('temperature', 0),
                        'oxygen_saturation': vital_info.get('oxygen_saturation', 0),
                        'respiratory_rate': vital_info.get('respiratory_rate', 0),
                        'timestamp': datetime.now()
                    }
                    
                    return self.vital_data
            
            return None
            
        except Exception as e:
            st.warning(f"⚠️ Error fetching vitals: {str(e)}")
            return None
    
    def start_continuous_monitoring(self):
        """Spin a background thread to poll regularly."""
        if self.data_thread and self.data_thread.is_alive():
            return
        
        self.stop_thread = False
        self.data_thread = threading.Thread(target=self._monitoring_loop)
        self.data_thread.daemon = True
        self.data_thread.start()
    
    def _monitoring_loop(self):
        """Small loop: if connected, fetch; then nap a sec."""
        while not self.stop_thread:
            if self.is_connected:
                self.get_latest_vitals()
            time.sleep(1)  # Check every second
    
    def get_current_vitals(self):
        """Return a copy of the latest snapshot."""
        # Fetch fresh data if connected
        if self.is_connected:
            self.get_latest_vitals()
        
        return self.vital_data.copy()
    
    def get_history(self, limit=100):
        """Ask the API for a recent history list, capped by limit."""
        try:
            response = requests.get(
                f"{self.api_url}/api/vitals/history",
                params={'limit': limit},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
            
            return []
            
        except Exception as e:
            st.warning(f"⚠️ Error fetching history: {str(e)}")
            return []
    
    def create_connection_ui(self):
        """Tiny UI to set API URL, connect, and see status/data."""
        st.subheader("📡 ESP32 WiFi Connection")
        
        # API URL configuration
        col1, col2 = st.columns(2)
        
        with col1:
            api_url = st.text_input(
                "API Server URL",
                value=self.api_url,
                help="URL of the API server (e.g., http://192.168.1.100:5000)"
            )
        
        with col2:
            st.write("")
            st.write("")
            if not self.is_connected:
                if st.button("🔗 Connect to API"):
                    self.api_url = api_url
                    self.connect()
            else:
                if st.button("🔌 Disconnect"):
                    self.disconnect()
        
        # Connection status
        self._display_connection_status()
        
        # Setup instructions
        with st.expander("📖 WiFi Setup Instructions"):
            st.markdown("""
            ### How to Set Up Wireless Connection:
            
            **Step 1: Configure ESP32**
            1. Open `esp32_monitor_wifi.ino` in Arduino IDE
            2. Change `WIFI_SSID` to your WiFi network name
            3. Change `WIFI_PASSWORD` to your WiFi password
            4. Find your computer's IP address:
               - Windows: Run `ipconfig` in Command Prompt
               - Look for "IPv4 Address" (e.g., 192.168.1.100)
            5. Update `API_ENDPOINT` in the code with your IP
            6. Upload to ESP32
            
            **Step 2: Start API Server**
            1. Open terminal in your project folder
            2. Run: `python api_server.py`
            3. Server will start on port 5000
            
            **Step 3: Connect**
            1. Make sure ESP32 is powered on
            2. Enter API URL above (use your computer's IP)
            3. Click "Connect to API"
            
            **Troubleshooting:**
            - Make sure ESP32 and computer are on same WiFi network
            - Check firewall isn't blocking port 5000
            - Use Serial Monitor to see ESP32 connection status
            """)
    
    def _display_connection_status(self):
        """Show if we’re connected and let you start monitoring."""
        if self.is_connected:
            st.success("🟢 Connected to API Server")
            
            # Start monitoring
            if st.button("📡 Start Wireless Monitoring"):
                self.start_continuous_monitoring()
                st.success("Wireless monitoring started!")
            
            # Display current data
            self._display_current_data()
            
            # Show server status
            try:
                response = requests.get(f"{self.api_url}/api/status", timeout=2)
                if response.status_code == 200:
                    status = response.json()
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Readings", status.get('total_readings', 0))
                    with col2:
                        st.metric("Queue Size", status.get('queue_size', 0))
                    with col3:
                        device = status.get('device_id', 'Unknown')
                        st.metric("Device ID", device)
            except:
                pass
        else:
            st.warning("🔴 Not connected to API server")
            st.info("💡 Start the API server first: `python api_server.py`")
    
    def _display_current_data(self):
        """Show the current vitals from WiFi so you know it’s working."""
        st.subheader("📊 Current WiFi Data")
        current_data = self.get_current_vitals()
        
        if current_data['timestamp']:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Heart Rate", f"{current_data['heart_rate']} BPM")
                st.metric("Temperature", f"{current_data['temperature']}°C")
            
            with col2:
                st.metric("Blood Pressure", 
                         f"{current_data['blood_pressure_systolic']}/"
                         f"{current_data['blood_pressure_diastolic']} mmHg")
                st.metric("Oxygen Saturation", f"{current_data['oxygen_saturation']}%")
            
            with col3:
                st.metric("Respiratory Rate", f"{current_data['respiratory_rate']} breaths/min")
                st.metric("Last Update", current_data['timestamp'].strftime("%H:%M:%S"))
