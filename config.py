import serial.tools.list_ports
import os

def get_serial_ports():
    return [port.device for port in serial.tools.list_ports.comports()]

# In your Streamlit UI:
ports = get_serial_ports()


# AI API Configuration
# Set these as environment variables for security
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "your-api-key-here")
DEEPSEEK_API_BASE = "https://api.deepseek.com/v1"
DEEPSEEK_MODEL = "deepseek-chat"



# ESP32 serial communication settings
DEFAULT_ESP32_PORT = "COM3"  # Change this to match your system
DEFAULT_BAUDRATE = 115200    # Communication speed
ESP32_READ_INTERVAL = 1000   # How often to read data (milliseconds)

# =============================================================================
# VITAL SIGNS CONFIGURATION
# =============================================================================

# Normal ranges for vital signs (min, max)
VITAL_RANGES = {
    'heart_rate': (60, 100),           # Beats per minute
    'blood_pressure_systolic': (90, 140),   # mmHg (top number)
    'blood_pressure_diastolic': (60, 90),   # mmHg (bottom number)
    'temperature': (36.0, 37.5),       # Celsius
    'oxygen_saturation': (95, 100),    # Percentage
    'respiratory_rate': (12, 20)       # Breaths per minute
}

# =============================================================================
# USER INTERFACE CONFIGURATION
# =============================================================================

# Auto-refresh settings
AUTO_REFRESH_INTERVAL = 10  # How often to refresh the page (seconds)

# Data management
MAX_DATA_POINTS = 50       # Maximum number of data points to store
CHART_HEIGHT = 300         # Height of charts in pixels

# =============================================================================
# SYSTEM CONFIGURATION
# =============================================================================

# Debug and logging settings
DEBUG_MODE = False
LOG_LEVEL = "INFO"

# File paths for data export and logging
DATA_EXPORT_PATH = "exports/"
LOG_FILE_PATH = "logs/"

# =============================================================================
# COLOR SCHEME
# =============================================================================

# Main UI colors
UI_COLORS = {
    'primary': '#667eea',      # Main brand color
    'secondary': '#764ba2',    # Secondary brand color
    'success': '#28a745',      # Green for success messages
    'warning': '#ffc107',      # Yellow for warnings
    'danger': '#dc3545',       # Red for errors
    'info': '#17a2b8',         # Blue for information
    'light': '#f8f9fa',        # Light gray background
    'dark': '#343a40'          # Dark gray text
}

# Colors for different vital signs
VITAL_COLORS = {
    'heart_rate': '#FF6B6B',           # Red for heart rate
    'temperature': '#1e938b',          # Teal for temperature
    'blood_pressure': '#45B7D1',       # Blue for blood pressure
    'oxygen_saturation': '#96CEB4',    # Green for oxygen
    'respiratory_rate': '#FFEAA7',     # Yellow for respiratory rate
    'ecg': '#FF1744'                   # Deep red for ECG waveform
}