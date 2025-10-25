"""
Vital monitoring, but make it simple.
We grab vitals, keep a tidy history, and tell you if things look fine or not.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
from config import VITAL_RANGES, VITAL_COLORS, MAX_DATA_POINTS, CHART_HEIGHT
from utils.ui_helpers import display_vital_card
import random
import math

class VitalMonitor:
    def __init__(self):
        """Set up a fresh tracker with empty history. Nothing fancy."""
        # Rolling stash of vitals so we can plot and judge later
        self.vital_data = {
            'heart_rate': [],
            'blood_pressure_systolic': [],
            'blood_pressure_diastolic': [],
            'temperature': [],
            'oxygen_saturation': [],
            'respiratory_rate': [],
            'ecg_value': [],
            'ecg_leads_connected': [],
            'timestamp': []
        }
        

    
    def _add_data_to_history(self, vitals, timestamp):
        """Add new vital data to the historical record"""
        self.vital_data['heart_rate'].append(vitals['heart_rate'])
        self.vital_data['blood_pressure_systolic'].append(vitals['blood_pressure_systolic'])
        self.vital_data['blood_pressure_diastolic'].append(vitals['blood_pressure_diastolic'])
        self.vital_data['temperature'].append(vitals['temperature'])
        self.vital_data['oxygen_saturation'].append(vitals['oxygen_saturation'])
        self.vital_data['respiratory_rate'].append(vitals['respiratory_rate'])
        self.vital_data['ecg_value'].append(vitals.get('ecg_value', 0))
        self.vital_data['ecg_leads_connected'].append(vitals.get('ecg_leads_connected', False))
        self.vital_data['timestamp'].append(timestamp)
    
    def _trim_data_history(self):
        """Keep just the latest data so memory doesn’t spiral."""
        if len(self.vital_data['timestamp']) > MAX_DATA_POINTS:
            for vital_type in self.vital_data:
                self.vital_data[vital_type] = self.vital_data[vital_type][-MAX_DATA_POINTS:]
    
    def get_vital_status(self, vital_name, value):
        """Label a vital as normal, warning, or critical. Straight to the point."""
        if vital_name not in VITAL_RANGES:
            return "unknown", "⚪"
        
        min_normal, max_normal = VITAL_RANGES[vital_name]
        
        # Check if value is within normal range
        if min_normal <= value <= max_normal:
            return "normal", "🟢"
        
        # Check if value is critical (far outside normal range)
        critical_threshold_low = min_normal * 0.8
        critical_threshold_high = max_normal * 1.2
        
        if value < critical_threshold_low or value > critical_threshold_high:
            return "critical", "🔴"
        else:
            return "warning", "🟡"
    
    def create_vital_dashboard(self, vitals_data=None):
        """Render the cards and ECG. If there’s data, we show it. If not, we say so."""
        if vitals_data:
            # Add new data to our history
            self._add_data_to_history(vitals_data, vitals_data.get('timestamp', datetime.now()))
            
            # Keep only the most recent data points
            self._trim_data_history()
            
            # Three neat columns for the essentials
            col1, col2, col3 = st.columns(3)
            
            # Display vital signs in each column
            with col1:
                self._display_heart_rate_card(vitals_data)
                self._display_temperature_card(vitals_data)
            
            with col2:
                self._display_blood_pressure_card(vitals_data)
                self._display_oxygen_saturation_card(vitals_data)
            
            with col3:
                self._display_respiratory_rate_card(vitals_data)
            
            # ECG gets its own lane
            st.markdown("---")
            self.display_ecg_card(vitals_data)
        else:
            st.warning("No vital data available. Please connect to ESP32.")
    
    def _display_heart_rate_card(self, vitals):
        """Display heart rate in a styled card"""
        status, _ = self.get_vital_status('heart_rate', vitals['heart_rate'])
        display_vital_card(
            "Heart Rate", 
            vitals['heart_rate'], 
            "BPM", 
            VITAL_COLORS['heart_rate'], 
            status
        )
    
    def _display_temperature_card(self, vitals):
        """Display temperature in a styled card"""
        status, _ = self.get_vital_status('temperature', vitals['temperature'])
        display_vital_card(
            "Temperature", 
            vitals['temperature'], 
            "°C", 
            VITAL_COLORS['temperature'], 
            status
        )
    
    def _display_blood_pressure_card(self, vitals):
        """Display blood pressure in a styled card"""
        systolic = vitals['blood_pressure_systolic']
        diastolic = vitals['blood_pressure_diastolic']
        blood_pressure_text = f"{systolic}/{diastolic}"
        
        display_vital_card(
            "Blood Pressure", 
            blood_pressure_text, 
            "mmHg", 
            VITAL_COLORS['blood_pressure']
        )
    
    def _display_oxygen_saturation_card(self, vitals):
        """Display oxygen saturation in a styled card"""
        status, _ = self.get_vital_status('oxygen_saturation', vitals['oxygen_saturation'])
        display_vital_card(
            "Oxygen Saturation", 
            vitals['oxygen_saturation'], 
            "%", 
            VITAL_COLORS['oxygen_saturation'], 
            status
        )
    
    def _display_respiratory_rate_card(self, vitals):
        """Display respiratory rate in a styled card"""
        status, _ = self.get_vital_status('respiratory_rate', vitals['respiratory_rate'])
        display_vital_card(
            "Respiratory Rate", 
            vitals['respiratory_rate'], 
            "breaths/min", 
            VITAL_COLORS['respiratory_rate'], 
            status
        )
    
    def display_ecg_card(self, vitals):
        """Display ECG data with real-time waveform (theme-aware)"""
        theme = st.session_state.get('ui_theme', 'Classic')
        
        # Theme-aware title
        if theme == 'Classic':
            st.subheader("🫀 ECG Monitor (Electrocardiogram)")
        else:
            st.subheader("ECG Monitor (Electrocardiogram)")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Display ECG waveform if we have data
            if len(self.vital_data['ecg_value']) > 0:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    y=self.vital_data['ecg_value'][-50:],  # Last 50 readings
                    mode='lines',
                    line=dict(color='#FF1744', width=2.5),
                    name='ECG Signal'
                ))
                
                # Theme-specific chart styling
                if theme == 'Classic':
                    # Dark theme styling
                    fig.update_layout(
                        title=dict(
                            text='ECG Waveform',
                            font=dict(color='#FF1744', size=16)
                        ),
                        height=250,
                        xaxis_title='Sample',
                        yaxis_title='Amplitude',
                        showlegend=False,
                        plot_bgcolor='rgba(30, 41, 59, 0.5)',
                        paper_bgcolor='rgba(30, 41, 59, 0.3)',
                        font=dict(color='#e2e8f0'),
                        xaxis=dict(
                            gridcolor='rgba(255, 255, 255, 0.1)',
                            color='#94a3b8'
                        ),
                        yaxis=dict(
                            gridcolor='rgba(255, 255, 255, 0.1)',
                            color='#94a3b8'
                        ),
                        margin=dict(l=40, r=20, t=40, b=40)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    # Modern theme styling with card wrapper
                    fig.update_layout(
                        title=dict(
                            text='Real-time Cardiac Signal',
                            font=dict(color='#1e293b', size=14, family='sans-serif', weight=600)
                        ),
                        height=280,
                        xaxis_title='Time (samples)',
                        yaxis_title='Amplitude',
                        showlegend=False,
                        plot_bgcolor='#f8fafc',
                        paper_bgcolor='white',
                        font=dict(color='#64748b', family='sans-serif'),
                        xaxis=dict(
                            gridcolor='#e2e8f0',
                            color='#64748b',
                            showgrid=True,
                            zeroline=False
                        ),
                        yaxis=dict(
                            gridcolor='#e2e8f0',
                            color='#64748b',
                            showgrid=True,
                            zeroline=False
                        ),
                        margin=dict(l=50, r=20, t=50, b=50)
                    )
                    
                    # Wrap in card-style container
                    chart_html = f"""
                    <div style="
                        background: white;
                        border: 1px solid #e8edf2;
                        border-radius: 16px;
                        padding: 1.25rem;
                        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
                        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                        position: relative;
                        overflow: hidden;
                        margin-bottom: 1rem;
                    ">
                        <div style="
                            position: absolute;
                            top: 0;
                            left: 0;
                            width: 4px;
                            height: 100%;
                            background: #FF1744;
                        "></div>
                        <div style="
                            font-size: 0.85rem;
                            font-weight: 600;
                            color: #64748b;
                            text-transform: uppercase;
                            letter-spacing: 0.5px;
                            margin-bottom: 0.75rem;
                            margin-left: 0.5rem;
                        ">ECG WAVEFORM</div>
                    </div>
                    """
                    st.markdown(chart_html, unsafe_allow_html=True)
                    st.plotly_chart(fig, use_container_width=True, key="ecg_waveform_modern")
            else:
                if theme == 'Classic':
                    st.info("⚡ No ECG data available yet")
                else:
                    # Modern theme info card
                    info_html = """
                    <div style="
                        background: white;
                        border: 1px solid #e8edf2;
                        border-radius: 16px;
                        padding: 2rem;
                        text-align: center;
                        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
                    ">
                        <div style="font-size: 3rem; margin-bottom: 1rem;">📊</div>
                        <div style="color: #64748b; font-weight: 500;">No ECG data available yet</div>
                        <div style="color: #94a3b8; font-size: 0.85rem; margin-top: 0.5rem;">
                            Collecting cardiac signals...
                        </div>
                    </div>
                    """
                    st.markdown(info_html, unsafe_allow_html=True)
        
        with col2:
            ecg_status = vitals.get('ecg_leads_connected', False)
            ecg_value = vitals.get('ecg_value', 0)
            
            # Theme-specific status display
            if theme == 'Classic':
                # Dark theme with colored cards
                if ecg_status:
                    status_html = """
                    <div style="
                        background: rgba(16, 185, 129, 0.15);
                        border: 2px solid #10b981;
                        border-radius: 12px;
                        padding: 1rem;
                        text-align: center;
                        margin-bottom: 1rem;
                    ">
                        <div style="color: #34d399; font-weight: 600; font-size: 0.9rem;">
                            ✅ Leads Connected
                        </div>
                    </div>
                    """
                else:
                    status_html = """
                    <div style="
                        background: rgba(239, 68, 68, 0.15);
                        border: 2px solid #ef4444;
                        border-radius: 12px;
                        padding: 1rem;
                        text-align: center;
                        margin-bottom: 1rem;
                    ">
                        <div style="color: #f87171; font-weight: 600; font-size: 0.9rem;">
                            ❌ Leads Disconnected
                        </div>
                    </div>
                    """
                st.markdown(status_html, unsafe_allow_html=True)
                
                # ECG Value card
                value_html = f"""
                <div style="
                    background: rgba(30, 41, 59, 0.5);
                    border: 2px solid #FF1744;
                    border-radius: 12px;
                    padding: 1.5rem 1rem;
                    text-align: center;
                ">
                    <div style="color: #FF1744; font-size: 0.9rem; font-weight: 600; margin-bottom: 0.5rem;">
                        ECG VALUE
                    </div>
                    <div style="color: #FF1744; font-size: 2rem; font-weight: 700; text-shadow: 0 2px 12px rgba(255, 23, 68, 0.4);">
                        {ecg_value}
                    </div>
                    <div style="color: #94a3b8; font-size: 0.75rem; margin-top: 0.5rem;">
                        Cardiac Activity
                    </div>
                </div>
                """
                st.markdown(value_html, unsafe_allow_html=True)
            else:
                # Modern theme with clean card design matching other vitals
                # Connection Status Card
                if ecg_status:
                    status_html = """
                    <div style="
                        background: white;
                        border: 1px solid #e8edf2;
                        border-radius: 16px;
                        padding: 1.5rem;
                        margin-bottom: 0.75rem;
                        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
                        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                        position: relative;
                        overflow: hidden;
                    ">
                        <div style="
                            position: absolute;
                            top: 0;
                            left: 0;
                            width: 4px;
                            height: 100%;
                            background: #10b981;
                        "></div>
                        <div style="
                            font-size: 0.85rem;
                            font-weight: 600;
                            color: #64748b;
                            text-transform: uppercase;
                            letter-spacing: 0.5px;
                            margin-bottom: 0.5rem;
                        ">STATUS</div>
                        <div style="
                            font-size: 0.95rem;
                            font-weight: 600;
                            color: #10b981;
                        ">✓ Connected</div>
                    </div>
                    """
                else:
                    status_html = """
                    <div style="
                        background: white;
                        border: 1px solid #e8edf2;
                        border-radius: 16px;
                        padding: 1.5rem;
                        margin-bottom: 0.75rem;
                        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
                        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                        position: relative;
                        overflow: hidden;
                    ">
                        <div style="
                            position: absolute;
                            top: 0;
                            left: 0;
                            width: 4px;
                            height: 100%;
                            background: #ef4444;
                        "></div>
                        <div style="
                            font-size: 0.85rem;
                            font-weight: 600;
                            color: #64748b;
                            text-transform: uppercase;
                            letter-spacing: 0.5px;
                            margin-bottom: 0.5rem;
                        ">STATUS</div>
                        <div style="
                            font-size: 0.95rem;
                            font-weight: 600;
                            color: #ef4444;
                        ">✗ Disconnected</div>
                    </div>
                    """
                st.markdown(status_html, unsafe_allow_html=True)
                
                # ECG Value Card (matching vital card style)
                value_html = f"""
                <div style="
                    background: white;
                    border: 1px solid #e8edf2;
                    border-radius: 16px;
                    padding: 1.5rem;
                    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                    cursor: pointer;
                    position: relative;
                    overflow: hidden;
                ">
                    <div style="
                        position: absolute;
                        top: 0;
                        left: 0;
                        width: 4px;
                        height: 100%;
                        background: #FF1744;
                    "></div>
                    <div style="
                        font-size: 0.85rem;
                        font-weight: 600;
                        color: #64748b;
                        text-transform: uppercase;
                        letter-spacing: 0.5px;
                        margin-bottom: 0.75rem;
                    ">ECG AMPLITUDE</div>
                    <div style="display: flex; align-items: baseline;">
                        <span style="
                            font-size: 2rem;
                            font-weight: 700;
                            color: #FF1744;
                            line-height: 1;
                        ">{ecg_value}</span>
                        <span style="
                            font-size: 0.95rem;
                            font-weight: 500;
                            color: #94a3b8;
                            margin-left: 0.5rem;
                        ">ADC</span>
                    </div>
                    <div style="
                        margin-top: 0.75rem;
                        font-size: 0.75rem;
                        color: #94a3b8;
                    ">Cardiac electrical activity</div>
                </div>
                """
                st.markdown(value_html, unsafe_allow_html=True)
    
    def get_health_recommendations(self, vitals_data):
        """Generate health recommendations based on current vital signs"""
        recommendations = []
        
        # Check each vital sign and add recommendations
        recommendations.extend(self._check_heart_rate(vitals_data))
        recommendations.extend(self._check_blood_pressure(vitals_data))
        recommendations.extend(self._check_temperature(vitals_data))
        recommendations.extend(self._check_oxygen_saturation(vitals_data))
        recommendations.extend(self._check_respiratory_rate(vitals_data))
        
        # If all vitals are normal, give positive feedback
        if not recommendations:
            recommendations.append("✅ All your vital signs are within normal ranges. Keep up the good health habits!")
        
        return recommendations
    
    def _check_heart_rate(self, vitals):
        """Check heart rate and return recommendations if needed"""
        recommendations = []
        heart_rate = vitals['heart_rate']
        min_normal, max_normal = VITAL_RANGES['heart_rate']
        
        if heart_rate < min_normal:
            recommendations.append("⚠️ Your heart rate is below normal. Consider consulting a doctor if this persists.")
        elif heart_rate > max_normal:
            recommendations.append("⚠️ Your heart rate is elevated. Try deep breathing exercises to relax.")
        
        return recommendations
    
    def _check_blood_pressure(self, vitals):
        """Check blood pressure and return recommendations if needed"""
        recommendations = []
        
        # Check systolic pressure
        systolic = vitals['blood_pressure_systolic']
        systolic_min, systolic_max = VITAL_RANGES['blood_pressure_systolic']
        if systolic > systolic_max:
            recommendations.append("⚠️ Your systolic blood pressure is high. Consider reducing salt intake and stress.")
        
        # Check diastolic pressure
        diastolic = vitals['blood_pressure_diastolic']
        diastolic_min, diastolic_max = VITAL_RANGES['blood_pressure_diastolic']
        if diastolic > diastolic_max:
            recommendations.append("⚠️ Your diastolic blood pressure is elevated. Monitor your blood pressure regularly.")
        
        return recommendations
    
    def _check_temperature(self, vitals):
        """Check temperature and return recommendations if needed"""
        recommendations = []
        temperature = vitals['temperature']
        min_normal, max_normal = VITAL_RANGES['temperature']
        
        if temperature > max_normal:
            recommendations.append("🌡️ Your temperature is slightly elevated. Stay hydrated and rest.")
        
        return recommendations
    
    def _check_oxygen_saturation(self, vitals):
        """Check oxygen saturation and return recommendations if needed"""
        recommendations = []
        oxygen_sat = vitals['oxygen_saturation']
        min_normal, max_normal = VITAL_RANGES['oxygen_saturation']
        
        if oxygen_sat < min_normal:
            recommendations.append("⚠️ Your oxygen saturation is below normal. Consider consulting a healthcare provider.")
        
        return recommendations
    
    def _check_respiratory_rate(self, vitals):
        """Check respiratory rate and return recommendations if needed"""
        recommendations = []
        respiratory_rate = vitals['respiratory_rate']
        min_normal, max_normal = VITAL_RANGES['respiratory_rate']
        
        if respiratory_rate > max_normal:
            recommendations.append("⚠️ Your breathing rate is elevated. Try slow, deep breathing exercises.")
        
        return recommendations
    
    def simulate_esp32_data(self):
        """Generate realistic simulated vital sign data for testing"""
        current_time = datetime.now()
        simulated_vitals = self._generate_realistic_vitals()
        self._add_data_to_history(simulated_vitals, current_time)
        self._trim_data_history()
        simulated_vitals['timestamp'] = current_time
        return simulated_vitals

    def _generate_realistic_vitals(self):
        """Generate realistic vital sign values"""
        # Generate realistic ECG waveform with heartbeat pattern (QRS complex simulation)
        # Simulate 75 BPM (1.25 beats per second)
        current_time = time.time()
        t = current_time * 1.25  # Heartbeat frequency
        
        # Create QRS complex pattern
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
        
        return {
            'heart_rate': random.randint(60, 100),
            'blood_pressure_systolic': random.randint(110, 140),
            'blood_pressure_diastolic': random.randint(70, 90),
            'temperature': round(random.uniform(36.5, 37.5), 1),
            'oxygen_saturation': random.randint(95, 100),
            'respiratory_rate': random.randint(12, 20),
            'ecg_value': ecg_sim,
            'ecg_leads_connected': True
        }