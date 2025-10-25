"""
Main app that wires everything together. Pulls vitals, shows cards, does the AI bits.
One place to run the whole thing without getting lost.
"""

import streamlit as st
import time
import pandas as pd
from datetime import datetime

# Import our organized modules
from config import VITAL_RANGES, AUTO_REFRESH_INTERVAL
from core.vital_monitor import VitalMonitor
from core.ai_assistant import AIHealthAssistant
from core.esp32_interface import ESP32Interface
from core.health_analytics import HealthAnalytics
from core.emergency_alerts import EmergencyAlertSystem
from core.patient_profile import PatientProfile
from core.health_goals import HealthGoalsTracker
from core.notifications import NotificationSystem
from utils.ui_helpers import (
    apply_custom_css, 
    create_header, 
    create_sidebar_header,
    create_status_indicator,
    create_info_box,
    create_disclaimer,
    display_vital_card,
    display_clickable_vital_card
)

def setup_page_configuration():
    """Page title, layout, and some CSS to keep the UI snappy."""
    st.set_page_config(
        page_title="AI-Powered Vital Monitoring",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    apply_custom_css()
    
    st.markdown("""
        <style>
        /* Hide ALL running indicators and overlays */
        .stApp [data-testid="stStatusWidget"] {
            display: none !important;
            visibility: hidden !important;
        }
        
        /* Hide the main app loading overlay */
        .stApp > header + div[data-testid="stAppViewContainer"] > div:first-child > div[data-testid="stVerticalBlock"] {
            pointer-events: auto !important;
        }
        
        /* Hide spinner overlay */
        .stSpinner, .stSpinner > div {
            display: none !important;
            visibility: hidden !important;
        }
        
        /* Hide the gray overlay that appears on reruns */
        div[data-testid="stAppViewContainer"] > div:first-child::before {
            display: none !important;
        }
        
        /* Prevent the blocking behavior */
        .element-container {
            pointer-events: auto !important;
        }
        
        /* Hide "Running..." text if it appears */
        .stApp [data-testid="stAppRunning"] {
            display: none !important;
        }
        
        /* Ensure buttons remain clickable */
        button {
            pointer-events: auto !important;
        }
        
        /* Hide the top-right running indicator */
        header [data-testid="stStatusWidget"] {
            display: none !important;
        }
        
        /* Remove any overlay backgrounds */
        .overlayBtn {
            display: none !important;
        }
        </style>
    """, unsafe_allow_html=True)

def initialize_session_state():
    """Prep session state so the app doesn’t forget who it is between reruns."""
    if 'ui_theme' not in st.session_state:
        st.session_state.ui_theme = 'Classic'
    
    if 'vital_monitor' not in st.session_state:
        st.session_state.vital_monitor = VitalMonitor()
    if 'ai_assistant' not in st.session_state:
        st.session_state.ai_assistant = AIHealthAssistant()
    if 'esp32_interface' not in st.session_state:
        st.session_state.esp32_interface = ESP32Interface()
    if 'health_analytics' not in st.session_state:
        st.session_state.health_analytics = HealthAnalytics()
    if 'emergency_alerts' not in st.session_state:
        st.session_state.emergency_alerts = EmergencyAlertSystem()
    if 'patient_profile' not in st.session_state:
        st.session_state.patient_profile = PatientProfile()
    if 'health_goals' not in st.session_state:
        st.session_state.health_goals = HealthGoalsTracker()
    if 'notifications' not in st.session_state:
        st.session_state.notifications = NotificationSystem()
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    if 'data_source' not in st.session_state:
        st.session_state.data_source = "Simulated Data"
    if 'symptom_rules' not in st.session_state or not st.session_state.symptom_rules:
        st.session_state.symptom_rules = [
            {"name": "Fever", "description": "High temperature, possible infection.", "conditions": [
                {"vital": "temperature", "operator": ">", "value": 38.0}
            ]},
            {"name": "Tachycardia", "description": "Elevated heart rate, may indicate stress, fever, or cardiac issue.", "conditions": [
                {"vital": "heart_rate", "operator": ">", "value": 100}
            ]},
            {"name": "Bradycardia", "description": "Low heart rate, may indicate heart block or athlete's heart.", "conditions": [
                {"vital": "heart_rate", "operator": "<", "value": 60}
            ]},
            {"name": "Hypertension", "description": "High blood pressure, risk of stroke or heart disease.", "conditions": [
                {"vital": "blood_pressure_systolic", "operator": ">", "value": 140},
                {"vital": "blood_pressure_diastolic", "operator": ">", "value": 90}
            ]},
            {"name": "Hypotension", "description": "Low blood pressure, may cause dizziness or fainting.", "conditions": [
                {"vital": "blood_pressure_systolic", "operator": "<", "value": 90},
                {"vital": "blood_pressure_diastolic", "operator": "<", "value": 60}
            ]},
            {"name": "Hypoxemia", "description": "Low oxygen saturation, possible respiratory issue.", "conditions": [
                {"vital": "oxygen_saturation", "operator": "<", "value": 94}
            ]},
            {"name": "Tachypnea", "description": "Rapid breathing, may indicate infection, anxiety, or lung issue.", "conditions": [
                {"vital": "respiratory_rate", "operator": ">", "value": 20}
            ]},
            {"name": "Bradypnea", "description": "Slow breathing, may indicate drug effect or neurological issue.", "conditions": [
                {"vital": "respiratory_rate", "operator": "<", "value": 12}
            ]},
            {"name": "Sepsis Alert", "description": "Possible sepsis (infection + abnormal vitals).", "conditions": [
                {"vital": "temperature", "operator": ">", "value": 38.0},
                {"vital": "heart_rate", "operator": ">", "value": 90},
                {"vital": "respiratory_rate", "operator": ">", "value": 20}
            ]},
            {"name": "Heat Stroke", "description": "Dangerously high temperature and heart rate.", "conditions": [
                {"vital": "temperature", "operator": ">", "value": 40.0},
                {"vital": "heart_rate", "operator": ">", "value": 110}
            ]},
            {"name": "Possible COVID-19", "description": "Signs suggestive of COVID-19 infection.", "conditions": [
                {"vital": "temperature", "operator": ">", "value": 37.8},
                {"vital": "respiratory_rate", "operator": ">", "value": 20},
                {"vital": "oxygen_saturation", "operator": "<", "value": 95}
            ]},
            {"name": "Mild Hypothermia", "description": "Low body temperature.", "conditions": [
                {"vital": "temperature", "operator": "<", "value": 35.0}
            ]},
            {"name": "Prehypertension", "description": "Borderline high blood pressure.", "conditions": [
                {"vital": "blood_pressure_systolic", "operator": ">=", "value": 120},
                {"vital": "blood_pressure_systolic", "operator": "<=", "value": 139}
            ]},
            {"name": "Possible Anemia", "description": "Low oxygen and high heart rate.", "conditions": [
                {"vital": "oxygen_saturation", "operator": "<", "value": 95},
                {"vital": "heart_rate", "operator": ">", "value": 100}
            ]},
            {"name": "Possible Asthma Attack", "description": "Low oxygen, high respiratory rate.", "conditions": [
                {"vital": "oxygen_saturation", "operator": "<", "value": 94},
                {"vital": "respiratory_rate", "operator": ">", "value": 20}
            ]},
            {"name": "Shock", "description": "Critical condition with low blood pressure and elevated heart rate.", "conditions": [
                {"vital": "blood_pressure_systolic", "operator": "<", "value": 90},
                {"vital": "heart_rate", "operator": ">", "value": 100}
            ]}
        ]

def create_sidebar_controls():
    """Sidebar = connection, source picker, status, refresh. All the knobs."""
    with st.sidebar:
        create_sidebar_header("Device Settings")
        
        st.session_state.esp32_interface.create_connection_ui()
        st.markdown("---")
        create_data_source_selector()
        st.markdown("---")
        create_system_status_display()
        create_auto_refresh_settings()

def create_data_source_selector():
    """Pick your poison: simulated or ESP32. Radio buttons make it easy."""
    st.subheader("Data Source")
    
    if 'data_source' not in st.session_state:
        st.session_state.data_source = "Simulated Data"
    
    data_source = st.radio(
        "Select Data Source:",
        ["Simulated Data", "ESP32 Real Data"],
        index=0 if st.session_state.data_source == "Simulated Data" else 1,
        help="Choose between simulated data for testing or real ESP32 sensor data"
    )
    
    st.session_state.data_source = data_source
    
    if data_source == "Simulated Data":
        create_status_indicator("info", "Using Simulated Data - No ESP32 required")
    else:
        create_status_indicator("info", "Using ESP32 Real Data - ESP32 connection required")

def create_system_status_display():
    """Quick status lights so you know what’s alive."""
    st.subheader("System Status")
    
    data_source = st.session_state.get("data_source", "Simulated Data")
    if data_source == "Simulated Data":
        create_status_indicator("success", "Simulated Data Mode")
    else:
        if st.session_state.esp32_interface.is_connected:
            create_status_indicator("success", "ESP32 Connected")
        else:
            create_status_indicator("warning", "ESP32 Disconnected")
    
    if st.session_state.ai_assistant.test_api_connection():
        create_status_indicator("success", "AI API Connected")
    else:
        create_status_indicator("warning", "AI API Disconnected")

def create_auto_refresh_settings():
    """Auto-refresh knob. Or just hit the button and vibe."""
    auto_refresh = st.checkbox("Auto-refresh", value=False, help="Enable automatic page refresh")
    refresh_interval = st.slider("Refresh interval (seconds)", 5, 60, AUTO_REFRESH_INTERVAL, disabled=not auto_refresh)
    
    if not auto_refresh:
        if st.button("Refresh Now", help="Manually refresh the page", use_container_width=True):
            st.rerun()
    
    st.session_state.auto_refresh = auto_refresh
    st.session_state.refresh_interval = refresh_interval

def get_current_vital_data():
    """Fetch one snapshot from either simulator or ESP32, your choice."""
    data_source = st.session_state.get("data_source", "Simulated Data")
    
    if data_source == "Simulated Data":
        return get_simulated_vitals()
    elif data_source == "ESP32 Real Data":
        if st.session_state.esp32_interface.is_connected:
            return st.session_state.esp32_interface.get_current_vitals()
        else:
            st.warning("⚠️ ESP32 not connected. Please connect to ESP32 to view real vital data.")
            return None
    else:
        return get_simulated_vitals()

@st.cache_data(ttl=1, show_spinner=False)
def get_simulated_vitals():
    """Fake it realistically so you can test without hardware."""
    import random
    import time
    import math
    
    
    current_time = time.time()
    
    
    base_temp = 36.5 + random.uniform(-0.5, 1.0)  # 36.0-37.5°C
    base_hr = 70 + random.randint(-10, 30)  # 60-100 BPM
    base_sys_bp = 110 + random.randint(-20, 30)  # 90-140 mmHg
    base_dia_bp = 70 + random.randint(-10, 20)  # 60-90 mmHg
    base_spo2 = 96 + random.randint(0, 4)  # 96-100%
    base_rr = 14 + random.randint(-2, 6)  # 12-20 breaths/min
    
 
    t = current_time * 1.25  # Heartbeat frequency
    

    beat_cycle = (t % 1.0)  # Position in current heartbeat (0-1)
    
    # Generate P wave, QRS complex, and T wave pattern
    if 0 <= beat_cycle < 0.15:  # P wave (small bump before spike)
        ecg_sim = int(2048 + 150 * math.sin(beat_cycle * 20))
    elif 0.15 <= beat_cycle < 0.35:  # QRS complex (large spike)
        spike_pos = (beat_cycle - 0.15) / 0.2
        ecg_sim = int(2048 + 800 * math.sin(spike_pos * math.pi))
    elif 0.35 <= beat_cycle < 0.55:  # T wave (smaller wave after spike)
        t_pos = (beat_cycle - 0.35) / 0.2
        ecg_sim = int(2048 + 200 * math.sin(t_pos * math.pi))
    else:  # Baseline (flat line between beats)
        ecg_sim = int(2048 + random.randint(-20, 20))  # Add small noise
    
    # Add some time-based variation to make it more realistic
    time_factor = int(current_time) % 60  # Changes every minute
    
    # Simulate some realistic patterns
    if time_factor < 10:
        # Simulate morning vitals (slightly elevated)
        base_hr += 5
        base_temp += 0.1
    elif time_factor < 30:
        # Simulate normal daytime vitals
        pass
    elif time_factor < 45:
        # Simulate post-exercise vitals (elevated)
        base_hr += 15
        base_rr += 3
    else:
        # Simulate evening vitals (slightly lower)
        base_hr -= 5
        base_temp -= 0.1
    
    return {
        "temperature": round(base_temp, 1),
        "heart_rate": int(base_hr),
        "blood_pressure_systolic": int(base_sys_bp),
        "blood_pressure_diastolic": int(base_dia_bp),
        "oxygen_saturation": int(base_spo2),
        "respiratory_rate": int(base_rr),
        "ecg_value": ecg_sim,
        "ecg_leads_connected": True
    }

def create_live_vitals_tab():
    """Live vitals tab: status banner, controls, and the dashboard."""
    st.subheader("Real-time Vital Monitoring")
    
    # Show data source with better indicators
    data_source = st.session_state.get("data_source", "Simulated Data")
    if data_source == "Simulated Data":
        create_status_indicator("info", "Using Simulated Data - No ESP32 Required")
    else:
        if st.session_state.esp32_interface.is_connected:
            create_status_indicator("success", "Using ESP32 Real Data - Connected")
        else:
            create_status_indicator("warning", "ESP32 Real Data Selected - Not Connected")
    # Real-time update controls
    create_realtime_controls()
    
    # Create containers for dynamic updates
    create_dynamic_vital_dashboard()

def create_realtime_controls():
    """Switch for real-time, a speed slider, and a manual refresh. Simple."""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Real-time update toggle
        realtime_enabled = st.checkbox(
            "Real-time Updates", 
            value=st.session_state.get("realtime_enabled", False),
            help="Enable continuous vital sign updates without page refresh"
        )
        st.session_state.realtime_enabled = realtime_enabled
    
    with col2:
        # Update frequency slider
        if realtime_enabled:
            update_frequency = st.slider(
                "Update Frequency (seconds)", 
                1, 10, 
                st.session_state.get("update_frequency", 2),
                help="How often to update the vital signs"
            )
            st.session_state.update_frequency = update_frequency
        else:
            create_status_indicator("info", "Real-time updates disabled")
    
    with col3:
        # Manual refresh button
        if st.button("Update Now", help="Manually update vital signs", use_container_width=True):
            st.session_state.manual_refresh = True
            st.rerun()

def create_dynamic_vital_dashboard():
    """Render the cards + ECG; keeps up with new data as it comes in."""
    # Initialize container for dynamic updates
    if 'dashboard_container' not in st.session_state:
        st.session_state.dashboard_container = st.empty()

    # Get current vital data (newly fetched this run)
    current_vitals = get_current_vital_data()

    # Cache the last fetched vitals to session state
    if current_vitals is not None:
        st.session_state['last_vitals'] = current_vitals
        # Add timestamp if not present
        if 'timestamp' not in current_vitals:
            from datetime import datetime
            current_vitals['timestamp'] = datetime.now()
        # Add data to VitalMonitor history for ECG waveform display
        st.session_state.vital_monitor._add_data_to_history(current_vitals, current_vitals['timestamp'])
        st.session_state.vital_monitor._trim_data_history()
    # Fallback: use cached data if current_vitals is None and we have old vitals
    cached_vitals = st.session_state.get('last_vitals')

    if current_vitals or cached_vitals:
        # Use current if available, else cached
        vitals_to_show = current_vitals if current_vitals is not None else cached_vitals
        with st.session_state.dashboard_container.container():
            col1, col2, col3 = st.columns(3)
            with col1:
                status, _ = st.session_state.vital_monitor.get_vital_status('heart_rate', vitals_to_show['heart_rate'])
                display_clickable_vital_card(
                    "Heart Rate", 
                    vitals_to_show['heart_rate'], 
                    "BPM", 
                    "#FF6B6B", 
                    status,
                    vital_key="heart_rate"
                )
                
                status, _ = st.session_state.vital_monitor.get_vital_status('temperature', vitals_to_show['temperature'])
                display_clickable_vital_card(
                    "Temperature",
                    vitals_to_show['temperature'],
                    "°C",
                    "#1e938b",
                    status,
                    vital_key="temperature"
                )
            
            with col2:
                systolic = vitals_to_show['blood_pressure_systolic']
                diastolic = vitals_to_show['blood_pressure_diastolic']
                blood_pressure_text = f"{systolic}/{diastolic}"
                
                # Blood Pressure Systolic
                status_sys, _ = st.session_state.vital_monitor.get_vital_status('blood_pressure_systolic', systolic)
                display_clickable_vital_card(
                    "Blood Pressure (Systolic)", 
                    systolic, 
                    "mmHg", 
                    "#45B7D1",
                    status_sys,
                    vital_key="blood_pressure_systolic"
                )
                
                status, _ = st.session_state.vital_monitor.get_vital_status('oxygen_saturation', vitals_to_show['oxygen_saturation'])
                display_clickable_vital_card(
                    "Oxygen Saturation", 
                    vitals_to_show['oxygen_saturation'],
                    "%", 
                    "#96CEB4",
                    status,
                    vital_key="oxygen_saturation"
                )
            
            with col3:
                status, _ = st.session_state.vital_monitor.get_vital_status('respiratory_rate', vitals_to_show['respiratory_rate'])
                display_clickable_vital_card(
                    "Respiratory Rate",
                    vitals_to_show['respiratory_rate'],
                    "breaths/min",
                    "#FFEAA7",
                    status,
                    vital_key="respiratory_rate"
                )
                
                # Add Blood Pressure Diastolic
                diastolic = vitals_to_show['blood_pressure_diastolic']
                status_dia, _ = st.session_state.vital_monitor.get_vital_status('blood_pressure_diastolic', diastolic)
                display_clickable_vital_card(
                    "Blood Pressure (Diastolic)",
                    diastolic,
                    "mmHg",
                    "#6C5CE7",
                    status_dia,
                    vital_key="blood_pressure_diastolic"
                )
            
            # Display ECG Monitor
            st.markdown("---")
            st.session_state.vital_monitor.display_ecg_card(vitals_to_show)
            
            st.subheader("AI Health Insights")
            recommendations = st.session_state.vital_monitor.get_health_recommendations(vitals_to_show)
            for recommendation in recommendations:
                # Clean up emojis from recommendations
                clean_rec = recommendation.replace("✅", "").replace("⚠️", "").replace("❌", "").strip()
                if "✅" in recommendation:
                    create_status_indicator("success", clean_rec)
                elif "⚠️" in recommendation:
                    create_status_indicator("warning", clean_rec)
                else:
                    create_status_indicator("info", clean_rec)
            integrate_with_new_systems(vitals_to_show)
            if current_vitals:  # Only run real-time or rerun logic if this was a live fetch
                handle_realtime_updates()
    else:
        data_source = st.session_state.get("data_source", "Simulated Data")
        if data_source == "Simulated Data":
            create_status_indicator("info", "Simulated data should be available. Please refresh or manually update vitals.")
        else:
            create_status_indicator("info", "Connect to ESP32 to view real vital signs data.")

def integrate_with_new_systems(vitals):
    """Integrate current vitals with all new systems"""
    # Add data to health analytics
    st.session_state.health_analytics.add_vital_data(vitals)
    
    # Check for emergency alerts
    alerts_triggered = st.session_state.emergency_alerts.check_vitals_for_alerts(vitals)
    
    # Update health goals progress
    st.session_state.health_goals.update_goal_progress(vitals)
    
    # Check for smart notifications
    smart_reminders = st.session_state.notifications.create_smart_reminders(vitals)
    
    # Check medication interactions
    if hasattr(st.session_state.patient_profile, 'check_medication_interactions'):
        interaction_warnings = st.session_state.patient_profile.check_medication_interactions(vitals)
        for warning in interaction_warnings:
            st.warning(warning)
    
    # Check and trigger regular reminders
    triggered_reminders = st.session_state.notifications.check_and_trigger_reminders()


def handle_realtime_updates():
    """If real-time is on, we count down and rerun on a loop. Chill timing."""
    # Disable automatic real-time updates by default to prevent lag
    # Users can manually refresh using the "Update Now" button
    if st.session_state.get("realtime_enabled", False):  # Changed from True to False
        update_frequency = st.session_state.get("update_frequency", 5)  # Increased from 2 to 5 seconds
        
        # Use st.empty() to create a placeholder for the countdown
        countdown_container = st.empty()
        
        # Show countdown and update
        for i in range(update_frequency, 0, -1):
            with countdown_container:
                st.info(f"⏱️ Next update in {i} seconds...")
            time.sleep(1)
        
        # Clear countdown and trigger update
        countdown_container.empty()
        st.rerun()

def create_ai_assistant_tab():
    """Create the AI assistant chat tab"""
    st.subheader(" AI Health Assistant")
    st.write("Ask me about your health concerns. I'll analyze your vital signs and provide personalized advice.")
    
    # Display chat history
    display_chat_history()
    
    # Handle new chat input
    handle_chat_input()
    
    # Chat control buttons
    create_chat_controls()

def display_chat_history():
    """Display the chat message history"""
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

def handle_chat_input():
    """Handle new chat input from the user"""
    user_prompt = st.chat_input("Describe your health concern:")
    if user_prompt:
        st.session_state.chat_messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)
        current_vitals = get_current_vital_data()
        # Check for rule matches
        rule_matches = match_symptom_rules(current_vitals, st.session_state.symptom_rules)
        # Pass matches to AI assistant
        ai_extra = f"\nPossible matches based on your vitals: {', '.join(rule_matches)}" if rule_matches else ""
        if current_vitals:
            ai_response = st.session_state.ai_assistant.analyze_vitals_with_ai(current_vitals, user_prompt + ai_extra)
        else:
            ai_response = st.session_state.ai_assistant.analyze_vitals_with_ai(None, user_prompt + ai_extra)
        st.session_state.chat_messages.append({"role": "assistant", "content": ai_response})
        with st.chat_message("assistant"):
            st.markdown(ai_response)

def create_chat_controls():
    """Create buttons for chat management"""
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_messages = []
    
    with col2:
        if st.button("📋 Export Chat"):
            export_chat_history()

def export_chat_history():
    """Export chat history to a text file"""
    chat_text = "\n\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.chat_messages])
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"health_chat_{timestamp}.txt"
    
    st.download_button(
        label="📥 Download Chat",
        data=chat_text,
        file_name=filename,
        mime="text/plain"
    )

def create_analytics_tab():
    """Create the enhanced analytics and trends tab"""
    st.subheader("📈 Advanced Health Analytics")
    
    # Use the new HealthAnalytics system
    st.session_state.health_analytics.create_health_summary()
    
    st.subheader("📊 Trend Analysis")
    st.session_state.health_analytics.create_trend_charts()
    
    st.subheader("🔍 Correlation Analysis")
    st.session_state.health_analytics.create_correlation_analysis()
    
    st.subheader("📤 Export Reports")
    st.session_state.health_analytics.export_health_data()

def create_emergency_alerts_tab():
    """Create emergency alerts tab"""
    st.session_state.emergency_alerts.create_alert_dashboard()
    
    st.subheader("🎯 Critical Thresholds")
    st.session_state.emergency_alerts.create_critical_thresholds_editor()

def create_patient_profile_tab():
    """Create patient profile tab"""
    st.session_state.patient_profile.create_profile_dashboard()

def create_health_goals_tab():
    """Create health goals tab"""
    st.session_state.health_goals.create_goals_dashboard()

def create_notifications_tab():
    """Create notifications tab"""
    st.session_state.notifications.create_notifications_dashboard()

def create_vital_statistics():
    """Create the vital statistics display"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Vital Statistics")
        
        # Calculate heart rate statistics
        heart_rate_data = st.session_state.vital_monitor.vital_data['heart_rate']
        average_heart_rate = sum(heart_rate_data) / len(heart_rate_data)
        max_heart_rate = max(heart_rate_data)
        min_heart_rate = min(heart_rate_data)
        
        # Display metrics
        st.metric("Average Heart Rate", f"{average_heart_rate:.1f} BPM")
        st.metric("Max Heart Rate", f"{max_heart_rate} BPM")
        st.metric("Min Heart Rate", f"{min_heart_rate} BPM")
        
        # Calculate and display health score
        health_score = calculate_health_score(average_heart_rate, max_heart_rate)
        st.metric("Health Score", f"{health_score}/100")

def calculate_health_score(average_hr, max_hr):
    """Calculate a simple health score based on heart rate data"""
    health_score = 100
    
    # Deduct points for abnormal heart rates
    if not (60 <= average_hr <= 100):
        health_score -= 20
    if max_hr > 120:
        health_score -= 10
    
    return health_score

def create_trend_analysis():
    """Create the trend analysis display"""
    col1, col2 = st.columns(2)
    
    with col2:
        st.subheader("📈 Trend Analysis")
        
        heart_rate_data = st.session_state.vital_monitor.vital_data['heart_rate']
        if len(heart_rate_data) >= 2:
            # Calculate recent vs overall average
            overall_average = sum(heart_rate_data) / len(heart_rate_data)
            recent_average = sum(heart_rate_data[-5:]) / len(heart_rate_data[-5:])
            
            # Show trend direction
            if recent_average > overall_average:
                st.warning("📈 Heart rate trending upward")
            elif recent_average < overall_average:
                st.success("📉 Heart rate trending downward")
            else:
                st.info("➡️ Heart rate stable")

def create_data_export_section():
    """Create the data export section"""
    st.subheader("📤 Export Data")
    if st.button("📊 Export Vital Data"):
        export_vital_data()

def export_vital_data():
    """Export vital data to CSV format"""
    # Create DataFrame from vital data
    vital_df = pd.DataFrame(st.session_state.vital_monitor.vital_data)
    csv_data = vital_df.to_csv(index=False)
    
    # Create download button
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"vital_data_{timestamp}.csv"
    
    st.download_button(
        label="📥 Download CSV",
        data=csv_data,
        file_name=filename,
        mime="text/csv"
    )

def create_settings_tab():
    """Create the system settings tab"""
    st.subheader("System Settings")
    
    # UI Theme Selector
    create_ui_theme_selector()
    
    st.markdown("---")
    
    # Data source is now controlled from the sidebar
    st.info("Data source selection is available in the sidebar")
    
    col1, col2 = st.columns(2)
    with col1:
        create_hardware_settings()
    with col2:
        create_ai_settings()
    create_system_information()

def create_ui_theme_selector():
    """Create UI theme selection interface"""
    st.subheader("🎨 User Interface Theme")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Theme selector
        current_theme = st.session_state.get('ui_theme', 'Classic')
        selected_theme = st.radio(
            "Select UI Theme:",
            ["Modern", "Classic"],
            index=0 if current_theme == "Modern" else 1,
            help="Choose between Modern (clean, minimal) or Classic (original with emojis)"
        )
        
        # Update theme if changed
        if selected_theme != current_theme:
            st.session_state.ui_theme = selected_theme
            st.success(f"✅ Theme changed to {selected_theme}!")
    
    with col2:
        # Theme preview/description
        if selected_theme == "Modern":
            st.markdown("""
            **Modern Theme:**
            - Light, clean design
            - White cards with colored borders
            - No emoji clutter
            - Professional appearance
            """)
        else:
            st.markdown("""
            **Classic Theme:**
            - Dark background theme
            - Colored borders & pulsing dots
            - Emoji indicators in tabs
            - Original design
            
            💡 **Enable dark mode for best experience:**
            Click ☰ (top-right) → Settings → Theme → Dark
            """)
    
    st.info(f"Current Theme: **{st.session_state.get('ui_theme', 'Classic')}**")

def create_hardware_settings():
    """Create hardware configuration settings"""
    st.subheader("🔧 Hardware Settings")
    
    # ESP32 settings
    st.write("**ESP32 Configuration:**")
    st.text_input("Serial Port", value=st.session_state.esp32_interface.port)
    st.selectbox("Baud Rate", [9600, 19200, 38400, 57600, 115200], index=4, key="baud_rate_selectbox_sidebar")
    
    # Sensor calibration
    st.write("**Sensor Calibration:**")
    st.number_input("Temperature Offset (°C)", value=0.0, step=0.1)
    st.number_input("Heart Rate Offset (BPM)", value=0, step=1)

def create_ai_settings():
    """Create AI configuration settings"""
    st.subheader(" AI Settings")
    
    # DEEPSEEK settings
    st.write("**DEEPSEEK Configuration:**")
    api_key = st.text_input("API Key", type="password", value=st.session_state.ai_assistant.api_key)
    if api_key != st.session_state.ai_assistant.api_key:
        st.session_state.ai_assistant.api_key = api_key
    
    # AI parameters
    st.write("**AI Parameters:**")
    st.slider("Response Length", 50, 500, 150)
    st.slider("Creativity", 0.0, 1.0, 0.7, step=0.1)

def create_system_information():
    """Display system information"""
    st.subheader("ℹ️ System Information")
    st.write(f"**Version:** 2.0.0")
    st.write(f"**Data Source:** {st.session_state.data_source}")
    st.write(f"**ESP32 Status:** {'Connected' if st.session_state.esp32_interface.is_connected else 'Disconnected'}")
    st.write(f"**Auto-refresh:** {'Enabled' if st.session_state.auto_refresh else 'Disabled'}")

def create_symptom_rules_tab():
    """Create the Symptom Rules dashboard for mapping vitals to diseases/infections"""
    st.subheader("🛠️ Symptom-to-Disease Rules Dashboard")
    st.write("""
    Configure rules that map vital sign patterns to possible diseases or infections. The AI assistant will use these rules to help detect conditions based on your vitals.
    """)
    
    # --- Add New Rule ---
    with st.expander("➕ Add New Rule", expanded=False):
        with st.form("add_rule_form", clear_on_submit=True):
            name = st.text_input("Disease/Infection Name")
            description = st.text_area("Description/Symptoms")
            st.markdown("**Vital Sign Conditions** (e.g., HR > 100, Temp > 38°C)")
            condition_cols = st.columns(4)
            vital_options = list(VITAL_RANGES.keys())
            with condition_cols[0]:
                vital = st.selectbox("Vital", vital_options, key="add_vital")
            with condition_cols[1]:
                operator = st.selectbox("Operator", [">", ">=", "<", "<=", "=="], key="add_operator")
            with condition_cols[2]:
                value = st.number_input("Value", value=0.0, key="add_value")
            with condition_cols[3]:
                add_condition = st.form_submit_button("Add Condition")
            # Store conditions in session temp
            if 'new_rule_conditions' not in st.session_state:
                st.session_state.new_rule_conditions = []
            if add_condition:
                st.session_state.new_rule_conditions.append({
                    "vital": vital,
                    "operator": operator,
                    "value": value
                })
                st.experimental_rerun()
            # Show current conditions
            if st.session_state.new_rule_conditions:
                st.write("**Current Conditions:**")
                for idx, cond in enumerate(st.session_state.new_rule_conditions):
                    st.write(f"{cond['vital']} {cond['operator']} {cond['value']}")
                if st.button("Clear Conditions", key="clear_conditions"):
                    st.session_state.new_rule_conditions = []
                    st.experimental_rerun()
            # Submit rule
            submitted = st.form_submit_button("Save Rule")
            if submitted and name and st.session_state.new_rule_conditions:
                st.session_state.symptom_rules.append({
                    "name": name,
                    "description": description,
                    "conditions": st.session_state.new_rule_conditions.copy()
                })
                st.session_state.new_rule_conditions = []
                st.success(f"Rule '{name}' added!")
                st.experimental_rerun()
    # --- List/Edit/Delete Rules ---
    st.markdown("---")
    st.subheader("Configured Rules")
    if not st.session_state.symptom_rules:
        st.info("No rules configured yet.")
    for idx, rule in enumerate(st.session_state.symptom_rules):
        with st.expander(f"{rule['name']}"):
            st.write(f"**Description:** {rule['description']}")
            st.write("**Conditions:**")
            for cond in rule['conditions']:
                st.write(f"- {cond['vital']} {cond['operator']} {cond['value']}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Delete Rule {idx}", key=f"delete_rule_{idx}"):
                    st.session_state.symptom_rules.pop(idx)
                    st.success("Rule deleted.")
                    st.experimental_rerun()
            # (Optional: Add edit functionality here)

def match_symptom_rules(vitals, rules):
    """Return a list of rule names that match the current vitals"""
    matches = []
    if not vitals:
        return matches
    for rule in rules:
        match = True
        for cond in rule['conditions']:
            vital_val = vitals.get(cond['vital'])
            if vital_val is None:
                match = False
                break
            op = cond['operator']
            val = cond['value']
            if op == ">" and not (vital_val > val):
                match = False
            elif op == ">=" and not (vital_val >= val):
                match = False
            elif op == "<" and not (vital_val < val):
                match = False
            elif op == "<=" and not (vital_val <= val):
                match = False
            elif op == "==" and not (vital_val == val):
                match = False
        if match:
            matches.append(rule['name'])
    return matches

def main():
    """Main application function - orchestrates all components"""
    # Set up the page
    setup_page_configuration()
    
    # Initialize session state
    initialize_session_state()
    
    # Create main header
    create_header(
        "AI-Powered Vital Monitoring System",
        "Real-time health monitoring with intelligent AI analysis"
    )
    
    # Create sidebar
    create_sidebar_controls()
    
    # Create main content tabs (with or without emojis based on theme)
    if st.session_state.get('ui_theme', 'Classic') == 'Modern':
        tab_names = [
            "📊 Live Vitals", 
            "🤖 AI Assistant", 
            "📈 Analytics", 
            "🚨 Emergency Alerts",
            "👤 Patient Profile",
            "🎯 Health Goals",
            "🔔 Notifications",
            "⚙️ Settings",
            "📋 Symptom Rules"
        ]
    else:
        tab_names = [
            "Live Vitals", 
            "AI Assistant", 
            "Analytics", 
            "Emergency Alerts",
            "Patient Profile",
            "Health Goals",
            "Notifications",
            "Settings",
            "Symptom Rules"
        ]
    
    # Use radio buttons instead of tabs for lazy loading
    # Store selected tab in session state
    if 'selected_tab' not in st.session_state:
        st.session_state.selected_tab = tab_names[0]
    
    # Style radio buttons to look like tabs
    st.markdown("""
    <style>
    div[data-testid="stRadio"] > div {
        background-color: rgba(28, 131, 225, 0.1);
        border-radius: 10px;
        padding: 0.5rem;
    }
    div[data-testid="stRadio"] > div > label {
        padding: 0.5rem 1rem;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    div[data-testid="stRadio"] > div > label:hover {
        background-color: rgba(28, 131, 225, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create tab selector with callback for smoother transitions
    def on_tab_change():
        st.session_state.selected_tab = st.session_state.tab_selector
    
    selected_tab = st.radio(
        "", 
        tab_names, 
        horizontal=True, 
        key='tab_selector',
        on_change=on_tab_change,
        label_visibility='collapsed',
        index=tab_names.index(st.session_state.selected_tab) if st.session_state.selected_tab in tab_names else 0
    )
    
    # Add visual separator
    st.markdown("---")
    
    # Only render the selected tab content (HUGE performance boost!)
    if "Live Vitals" in selected_tab:
        create_live_vitals_tab()
    elif "AI Assistant" in selected_tab:
        create_ai_assistant_tab()
    elif "Analytics" in selected_tab:
        create_analytics_tab()
    elif "Emergency Alerts" in selected_tab:
        create_emergency_alerts_tab()
    elif "Patient Profile" in selected_tab:
        create_patient_profile_tab()
    elif "Health Goals" in selected_tab:
        create_health_goals_tab()
    elif "Notifications" in selected_tab:
        create_notifications_tab()
    elif "Settings" in selected_tab:
        create_settings_tab()
    elif "Symptom Rules" in selected_tab:
        create_symptom_rules_tab()
    
    # Add footer disclaimer
    create_disclaimer()
    
    # Note: Real-time updates are handled within the live vitals tab

if __name__ == "__main__":
    main() 