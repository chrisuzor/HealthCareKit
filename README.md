# HealthCareKit

A comprehensive healthcare monitoring system that combines IoT hardware (ESP32) with a modern web interface for real-time vital signs monitoring, health analytics, and emergency alerts.

## 🏥 Features

### Core Functionality
- **Real-time Vital Monitoring**: Heart rate, blood pressure, temperature, and oxygen saturation tracking
- **AI-Powered Health Assistant**: Intelligent health insights and recommendations
- **Emergency Alert System**: Automatic alerts for critical health conditions
- **Health Analytics Dashboard**: Comprehensive data visualization and trend analysis
- **Patient Profile Management**: Secure patient data storage and management
- **Goal Tracking**: Health goal setting and progress monitoring
- **Notification System**: Multi-channel health notifications

### Hardware Integration
- **ESP32 Vital Monitor**: Arduino-based sensor integration
- **WiFi Connectivity**: Wireless data transmission
- **Serial Communication**: Direct hardware interface
- **Desktop Application**: Cross-platform desktop wrapper

## 🛠️ Technology Stack

### Backend
- **Python 3.10+**
- **Streamlit**: Web application framework
- **Flask**: REST API server
- **Pandas & NumPy**: Data processing and analysis
- **Plotly**: Interactive data visualization

### Hardware
- **ESP32 Microcontroller**: Sensor data collection
- **Arduino IDE**: Hardware programming
- **PySerial**: Serial communication

### Desktop Application
- **PyWebView**: Desktop app wrapper
- **PyInstaller**: Executable generation

## 📋 Prerequisites

- Python 3.10 or higher
- Arduino IDE (for ESP32 programming)
- ESP32 development board
- Vital signs sensors (heart rate, blood pressure, temperature, SpO2)

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd HealthCareKit
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Hardware Setup
1. Install Arduino IDE
2. Add ESP32 board support
3. Upload the code from `esp32_vital_monitor/` to your ESP32
4. Connect sensors to ESP32 according to the pin configuration

## 🏃‍♂️ Quick Start

### Web Application
```bash
# Activate virtual environment
source venv/bin/activate

# Run Streamlit app
streamlit run app.py
```

### API Server
```bash
# Run Flask API server
python api_server.py
```

### Desktop Application
```bash
# Run desktop app
python scripts/desktop_launcher.py
```

## 📁 Project Structure

```
HealthCareKit/
├── core/                    # Core application modules
│   ├── ai_assistant.py     # AI health assistant
│   ├── emergency_alerts.py # Emergency alert system
│   ├── health_analytics.py # Health data analysis
│   ├── health_goals.py     # Goal tracking
│   ├── notifications.py    # Notification system
│   ├── patient_profile.py  # Patient management
│   ├── vital_monitor.py    # Vital signs monitoring
│   └── esp32_interface.py  # ESP32 communication
├── esp32_vital_monitor/     # ESP32 Arduino code
│   ├── esp32_monitor/       # Basic monitor
│   └── esp32_monitor_wifi/  # WiFi-enabled monitor
├── scripts/                 # Utility scripts
│   ├── build_desktop_app.py # Desktop app builder
│   └── desktop_launcher.py  # Desktop launcher
├── tests/                   # Test files
├── utils/                   # Utility functions
├── app.py                   # Main Streamlit application
├── api_server.py           # Flask API server
├── config.py               # Configuration settings
└── requirements.txt        # Python dependencies
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:
```env
# API Configuration
API_HOST=localhost
API_PORT=5000

# Database Configuration
DATABASE_URL=sqlite:///healthcare.db

# Notification Settings
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password

# ESP32 Configuration
ESP32_PORT=/dev/ttyUSB0  # Linux/Mac
# ESP32_PORT=COM3        # Windows
ESP32_BAUDRATE=115200
```

### ESP32 Configuration
1. Update WiFi credentials in `esp32_vital_monitor/esp32_monitor_wifi/esp32_monitor_wifi.ino`
2. Configure sensor pins according to your hardware setup
3. Upload the code to your ESP32

## 📊 Usage

### Web Interface
1. Start the Streamlit app: `streamlit run app.py`
2. Open your browser to `http://localhost:8501`
3. Navigate through the different sections:
   - **Dashboard**: Real-time vital signs
   - **Analytics**: Health trends and insights
   - **Profile**: Patient information
   - **Goals**: Health goal tracking
   - **Alerts**: Emergency notifications

### API Endpoints
- `GET /api/vitals` - Get current vital signs
- `POST /api/vitals` - Submit new vital readings
- `GET /api/patient/{id}` - Get patient information
- `POST /api/alert` - Send emergency alert

### Desktop Application
1. Run `python scripts/desktop_launcher.py`
2. The application will open in a native window
3. All web features are available in the desktop version

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python tests/dependencies_test.py
```

## 📦 Building Desktop Application

### Windows
```bash
python scripts/build_desktop_app.py
```

### Cross-platform
```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller --onefile --windowed app.py
```

## 🔒 Security Considerations

- Patient data is stored locally by default
- Implement proper authentication for production use
- Use HTTPS for web interfaces
- Encrypt sensitive health data
- Regular security updates for dependencies

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Add tests for new functionality
5. Commit your changes: `git commit -m 'Add new feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation in the `docs/` folder
- Review the test files for usage examples

## 🔮 Roadmap

- [ ] Mobile app integration
- [ ] Cloud data synchronization
- [ ] Advanced AI health predictions
- [ ] Multi-language support
- [ ] Integration with popular fitness trackers
- [ ] Telemedicine features

## 📈 Performance

- Real-time data processing with minimal latency
- Efficient data storage and retrieval
- Optimized for low-power ESP32 operation
- Responsive web interface with caching

---

**Note**: This is a healthcare application. Always consult with medical professionals for health-related decisions. This software is for monitoring and informational purposes only.
