"""
Talks to the ESP32 over serial. We read lines, parse JSON, and stash vitals.
No drama, just data in and data out.
"""

import serial
import json
import time
import threading
from datetime import datetime
import streamlit as st
from config import DEFAULT_ESP32_PORT, DEFAULT_BAUDRATE, ESP32_READ_INTERVAL

class ESP32Interface:
    def __init__(self, port=DEFAULT_ESP32_PORT, baudrate=DEFAULT_BAUDRATE):
        """
        Set up serial settings and a clean vitals buffer.
        Args:
            port (str): e.g., 'COM3' (Windows) or '/dev/ttyUSB0' (Linux)
            baudrate (int): serial speed, keep it matched with the sketch
        """
        self.port = port
        self.baudrate = baudrate
        self.serial_connection = None
        self.is_connected = False
        
        # Store current vital data
        self.vital_data = self._initialize_vital_data()
        
        # Threading variables for continuous monitoring
        self.data_thread = None
        self.stop_thread = False
        
    def _initialize_vital_data(self):
        """Make a default vitals dict so we always have something to show."""
        return {
            'heart_rate': 0,
            'blood_pressure_systolic': 0,
            'blood_pressure_diastolic': 0,
            'temperature': 0,
            'oxygen_saturation': 0,
            'respiratory_rate': 0,
            'ecg_value': 0,
            'ecg_leads_connected': False,
            'timestamp': None
        }
        
    def connect(self):
        """Open the serial port and hope the board says hi."""
        try:
            # Create serial connection
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1
            )
            self.is_connected = True
            st.success(f"✅ Connected to ESP32 on {self.port}")
            return True
        except Exception as e:
            st.error(f"❌ Failed to connect to ESP32: {str(e)}")
            return False
    
    def disconnect(self):
        """Shut the port, stop the thread, keep it tidy."""
        # Stop the monitoring thread
        self.stop_thread = True
        
        # Close the serial connection
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
        
        self.is_connected = False
        st.info("🔌 Disconnected from ESP32")
    
    def send_command(self, command):
        """Write a line to the board. It’s listening, hopefully."""
        if not self.is_connected or not self.serial_connection:
            return False
        
        try:
            # Send command with newline
            self.serial_connection.write(f"{command}\n".encode())
            return True
        except Exception as e:
            st.error(f"Error sending command: {str(e)}")
            return False
    
    def read_vital_data(self):
        """Try to grab one JSON line and parse it into vitals."""
        if not self.is_connected or not self.serial_connection:
            return None
        
        try:
            # Check if there's data waiting to be read
            if self.serial_connection.in_waiting:
                # Read one line of data
                data_line = self.serial_connection.readline().decode('utf-8').strip()
                if data_line:
                    return self.parse_vital_data(data_line)
        except Exception as e:
            st.error(f"Error reading data: {str(e)}")
        
        return None
    
    def parse_vital_data(self, data_string):
        """json.loads, then map fields into our format. No mystery here."""
        try:
            
            json_data = json.loads(data_string)
            
            # Update vital data with parsed values
            self.vital_data = {
                'heart_rate': json_data.get('hr', 0),
                'blood_pressure_systolic': json_data.get('bp_sys', 0),
                'blood_pressure_diastolic': json_data.get('bp_dia', 0),
                'temperature': json_data.get('temp', 0),
                'oxygen_saturation': json_data.get('spo2', 0),
                'respiratory_rate': json_data.get('rr', 0),
                'ecg_value': json_data.get('ecg', 0),
                'ecg_leads_connected': json_data.get('ecg_leads', False),
                'timestamp': datetime.now()
            }
            
            return self.vital_data
        except json.JSONDecodeError:
            st.warning(" Invalid data format received from ESP32")
            return None
        except Exception as e:
            st.error(f"Error parsing data: {str(e)}")
            return None
    
    def start_continuous_monitoring(self):
        """Spin up a thread that reads in the background. Chill loop."""
        # Don't start if already monitoring
        if self.data_thread and self.data_thread.is_alive():
            return
        
        # Reset stop flag and start monitoring thread
        self.stop_thread = False
        self.data_thread = threading.Thread(target=self._monitoring_loop)
        self.data_thread.daemon = True
        self.data_thread.start()
    
    def _monitoring_loop(self):
        """Background read → parse → stash → repeat, with a short nap."""
        while not self.stop_thread:
            if self.is_connected:
                # Read data from ESP32
                data = self.read_vital_data()
                if data:
                    # Data is automatically stored in self.vital_data
                    pass
            
            # Wait before next reading
            time.sleep(ESP32_READ_INTERVAL / 1000)  # Convert milliseconds to seconds
    
    def get_current_vitals(self):
        """Return a copy so callers can’t mess with our internal dict."""
        return self.vital_data.copy()
    
    def create_connection_ui(self):
        """Tiny UI bits to connect/disconnect and peek at data."""
        st.subheader("🔌 ESP32 Connection")
        
        # Create two columns for connection controls
        col1, col2 = st.columns(2)
        
        with col1:
            # Port and baudrate inputs
            port = st.text_input("Serial Port", value=self.port, help="e.g., COM3 (Windows) or /dev/ttyUSB0 (Linux)")
            baudrate = st.selectbox("Baud Rate", [9600, 19200, 38400, 57600, 115200], index=4, key="baud_rate_selectbox_settings")
        
        with col2:
            # Connection buttons
            st.write("")  # Add some spacing
            st.write("")
            if not self.is_connected:
                if st.button("🔗 Connect to ESP32"):
                    self.port = port
                    self.baudrate = baudrate
                    self.connect()
            else:
                if st.button("🔌 Disconnect"):
                    self.disconnect()
        
        # Show connection status and data
        self._display_connection_status()
    
    def _display_connection_status(self):
        """Status panel plus a button to kick off monitoring."""
        if self.is_connected:
            st.success("🟢 Connected to ESP32")
            
            # Start monitoring button
            if st.button("📡 Start Monitoring"):
                self.start_continuous_monitoring()
                st.success("Monitoring started!")
            
            # Display current data
            self._display_current_data()
        else:
            st.warning("🔴 Not connected to ESP32")
            
            # Show available ports button
            if st.button("🔍 Scan for Available Ports"):
                self.scan_available_ports()
    
    def _display_current_data(self):
        """Show the latest numbers so you know it’s alive."""
        st.subheader(" Current ESP32 Data")
        current_data = self.get_current_vitals()
        
        if current_data['timestamp']:
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Heart Rate", f"{current_data['heart_rate']} BPM")
                st.metric("Temperature", f"{current_data['temperature']}°C")
            
            with col2:
                st.metric("Blood Pressure", f"{current_data['blood_pressure_systolic']}/{current_data['blood_pressure_diastolic']} mmHg")
                st.metric("Oxygen Saturation", f"{current_data['oxygen_saturation']}%")
            
            with col3:
                st.metric("Respiratory Rate", f"{current_data['respiratory_rate']} breaths/min")
                ecg_status = "✅ Connected" if current_data['ecg_leads_connected'] else "❌ Disconnected"
                st.metric("ECG", f"{current_data['ecg_value']} ({ecg_status})")
            
            st.metric("Last Update", current_data['timestamp'].strftime("%H:%M:%S"))
    
    def scan_available_ports(self):
        """List serial ports so you don’t have to guess COM names."""
        try:
            import serial.tools.list_ports
            available_ports = serial.tools.list_ports.comports()
            
            if available_ports:
                st.write("Available ports:")
                for port in available_ports:
                    st.write(f"- {port.device}: {port.description}")
            else:
                st.write("No serial ports found")
        except Exception as e:
            st.error(f"Error scanning ports: {str(e)}") 