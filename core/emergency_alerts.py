"""
Emergency Alert System Module
Handles critical vital monitoring and emergency notifications
"""

import streamlit as st
import time
import json
from datetime import datetime
from config import VITAL_RANGES

class EmergencyAlertSystem:
    def __init__(self):
        """Initialize the emergency alert system"""
        self.critical_thresholds = self._load_critical_thresholds()
        self.alert_history = self._load_alert_history()
        self.emergency_contacts = self._load_emergency_contacts()
        self.alert_settings = self._load_alert_settings()
        
    def _load_critical_thresholds(self):
        """Load critical vital thresholds"""
        if 'critical_thresholds' not in st.session_state:
            st.session_state.critical_thresholds = {
                'heart_rate': {'min': 40, 'max': 150},
                'blood_pressure_systolic': {'min': 70, 'max': 180},
                'blood_pressure_diastolic': {'min': 40, 'max': 110},
                'temperature': {'min': 35.0, 'max': 40.0},
                'oxygen_saturation': {'min': 85, 'max': 100},
                'respiratory_rate': {'min': 8, 'max': 30}
            }
        return st.session_state.critical_thresholds
    
    def _load_alert_history(self):
        """Load alert history"""
        if 'alert_history' not in st.session_state:
            st.session_state.alert_history = []
        return st.session_state.alert_history
    
    def _load_emergency_contacts(self):
        """Load emergency contacts"""
        if 'emergency_contacts' not in st.session_state:
            st.session_state.emergency_contacts = [
                {"name": "Emergency Services", "phone": "911", "type": "emergency"},
                {"name": "Primary Doctor", "phone": "", "type": "medical"},
                {"name": "Family Contact", "phone": "", "type": "family"}
            ]
        return st.session_state.emergency_contacts
    
    def _load_alert_settings(self):
        """Load alert settings"""
        if 'alert_settings' not in st.session_state:
            st.session_state.alert_settings = {
                'alerts_enabled': True,
                'audio_alerts': True,
                'visual_alerts': True,
                'auto_emergency_mode': True,
                'alert_cooldown': 300  # 5 minutes
            }
        return st.session_state.alert_settings
    
    def check_vitals_for_alerts(self, vitals):
        """Check vitals against critical thresholds and trigger alerts"""
        if not self.alert_settings['alerts_enabled']:
            return
        
        alerts_triggered = []
        current_time = datetime.now()
        
        for vital_name, value in vitals.items():
            if vital_name in self.critical_thresholds and value is not None:
                threshold = self.critical_thresholds[vital_name]
                
                # Check if value is outside critical range
                if value < threshold['min'] or value > threshold['max']:
                    alert_level = self._determine_alert_level(vital_name, value, threshold)
                    
                    # Check cooldown to prevent spam
                    if self._should_trigger_alert(vital_name, current_time):
                        alert = {
                            'vital': vital_name,
                            'value': value,
                            'threshold': threshold,
                            'level': alert_level,
                            'timestamp': current_time,
                            'message': self._generate_alert_message(vital_name, value, threshold, alert_level)
                        }
                        
                        alerts_triggered.append(alert)
                        self._trigger_alert(alert)
                        self._add_to_alert_history(alert)
        
        return alerts_triggered
    
    def _determine_alert_level(self, vital_name, value, threshold):
        """Determine alert severity level"""
        min_val, max_val = threshold['min'], threshold['max']
        
        # Calculate how far outside normal range
        if value < min_val:
            deviation = (min_val - value) / min_val
        else:
            deviation = (value - max_val) / max_val
        
        if deviation > 0.5:  # More than 50% deviation
            return 'critical'
        elif deviation > 0.2:  # More than 20% deviation
            return 'warning'
        else:
            return 'caution'
    
    def _should_trigger_alert(self, vital_name, current_time):
        """Check if enough time has passed since last alert for this vital"""
        cooldown = self.alert_settings['alert_cooldown']
        
        # Find last alert for this vital
        for alert in reversed(self.alert_history):
            if alert['vital'] == vital_name:
                time_diff = (current_time - alert['timestamp']).total_seconds()
                return time_diff > cooldown
        
        return True  # No previous alert found
    
    def _generate_alert_message(self, vital_name, value, threshold, level):
        """Generate alert message"""
        vital_display = vital_name.replace('_', ' ').title()
        
        if value < threshold['min']:
            condition = f"critically low ({value} < {threshold['min']})"
        else:
            condition = f"critically high ({value} > {threshold['max']})"
        
        level_emoji = {'critical': '🚨', 'warning': '⚠️', 'caution': '⚡'}
        
        return f"{level_emoji[level]} {vital_display} is {condition}"
    
    def _trigger_alert(self, alert):
        """Trigger visual and audio alerts"""
        if self.alert_settings['visual_alerts']:
            self._show_visual_alert(alert)
        
        if self.alert_settings['audio_alerts']:
            self._trigger_audio_alert(alert)
        
        # Auto-enable emergency mode for critical alerts
        if alert['level'] == 'critical' and self.alert_settings['auto_emergency_mode']:
            self._enable_emergency_mode()
    
    def _show_visual_alert(self, alert):
        """Show visual alert in Streamlit"""
        if alert['level'] == 'critical':
            st.error(f"🚨 CRITICAL ALERT: {alert['message']}")
        elif alert['level'] == 'warning':
            st.warning(f"⚠️ WARNING: {alert['message']}")
        else:
            st.info(f"⚡ CAUTION: {alert['message']}")
    
    def _trigger_audio_alert(self, alert):
        """Trigger audio alert (placeholder for future implementation)"""
        # This would integrate with browser audio APIs
        # For now, we'll use visual indicators
        pass
    
    def _enable_emergency_mode(self):
        """Enable emergency mode with enhanced monitoring"""
        st.session_state.emergency_mode = True
        st.error("🚨 EMERGENCY MODE ACTIVATED - Enhanced monitoring enabled")
    
    def _add_to_alert_history(self, alert):
        """Add alert to history"""
        self.alert_history.append(alert)
        
        # Keep only last 100 alerts
        if len(self.alert_history) > 100:
            self.alert_history = self.alert_history[-100:]
    
    def create_alert_dashboard(self):
        """Create emergency alert dashboard"""
        st.subheader("🚨 Emergency Alert System")
        
        # Alert status
        col1, col2, col3 = st.columns(3)
        
        with col1:
            alert_status = "🟢 Active" if self.alert_settings['alerts_enabled'] else "🔴 Disabled"
            st.metric("Alert Status", alert_status)
        
        with col2:
            emergency_mode = "🚨 ON" if st.session_state.get('emergency_mode', False) else "🟢 OFF"
            st.metric("Emergency Mode", emergency_mode)
        
        with col3:
            recent_alerts = len([a for a in self.alert_history if (datetime.now() - a['timestamp']).days < 1])
            st.metric("Alerts Today", recent_alerts)
        
        # Alert controls
        self._create_alert_controls()
        
        # Recent alerts
        self._show_recent_alerts()
        
        # Emergency contacts
        self._manage_emergency_contacts()
    
    def _create_alert_controls(self):
        """Create alert control settings"""
        st.subheader("⚙️ Alert Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            self.alert_settings['alerts_enabled'] = st.checkbox(
                "Enable Alerts", 
                value=self.alert_settings['alerts_enabled']
            )
            
            self.alert_settings['visual_alerts'] = st.checkbox(
                "Visual Alerts", 
                value=self.alert_settings['visual_alerts']
            )
            
            self.alert_settings['audio_alerts'] = st.checkbox(
                "Audio Alerts", 
                value=self.alert_settings['audio_alerts']
            )
        
        with col2:
            self.alert_settings['auto_emergency_mode'] = st.checkbox(
                "Auto Emergency Mode", 
                value=self.alert_settings['auto_emergency_mode']
            )
            
            cooldown_minutes = self.alert_settings['alert_cooldown'] // 60
            new_cooldown = st.slider(
                "Alert Cooldown (minutes)", 
                1, 60, 
                cooldown_minutes
            ) * 60
            self.alert_settings['alert_cooldown'] = new_cooldown
        
        # Manual emergency mode toggle
        if st.button("🚨 Toggle Emergency Mode"):
            st.session_state.emergency_mode = not st.session_state.get('emergency_mode', False)
            st.rerun()
    
    def _show_recent_alerts(self):
        """Show recent alert history"""
        st.subheader("📋 Recent Alerts")
        
        if not self.alert_history:
            st.info("No alerts triggered yet")
            return
        
        # Show last 10 alerts
        recent_alerts = self.alert_history[-10:]
        
        for alert in reversed(recent_alerts):
            time_ago = datetime.now() - alert['timestamp']
            
            if alert['level'] == 'critical':
                st.error(f"🚨 {alert['message']} ({time_ago.seconds//60} minutes ago)")
            elif alert['level'] == 'warning':
                st.warning(f"⚠️ {alert['message']} ({time_ago.seconds//60} minutes ago)")
            else:
                st.info(f"⚡ {alert['message']} ({time_ago.seconds//60} minutes ago)")
    
    def _manage_emergency_contacts(self):
        """Manage emergency contacts"""
        st.subheader("📞 Emergency Contacts")
        
        for i, contact in enumerate(self.emergency_contacts):
            col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
            
            with col1:
                name = st.text_input(f"Name {i+1}", value=contact['name'], key=f"contact_name_{i}")
                contact['name'] = name
            
            with col2:
                phone = st.text_input(f"Phone {i+1}", value=contact['phone'], key=f"contact_phone_{i}")
                contact['phone'] = phone
            
            with col3:
                contact_type = st.selectbox(
                    f"Type {i+1}", 
                    ["emergency", "medical", "family"], 
                    index=["emergency", "medical", "family"].index(contact['type']),
                    key=f"contact_type_{i}"
                )
                contact['type'] = contact_type
            
            with col4:
                if st.button("📞 Call", key=f"call_{i}"):
                    st.info(f"Calling {contact['name']} at {contact['phone']}")
        
        # Add new contact
        if st.button("➕ Add Emergency Contact"):
            self.emergency_contacts.append({
                "name": "New Contact",
                "phone": "",
                "type": "family"
            })
            st.rerun()
    
    def create_critical_thresholds_editor(self):
        """Create interface for editing critical thresholds"""
        st.subheader("🎯 Critical Thresholds")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Lower Limits (Critical Minimums)**")
            for vital in ['heart_rate', 'temperature', 'oxygen_saturation', 'respiratory_rate']:
                if vital in self.critical_thresholds:
                    current_min = self.critical_thresholds[vital]['min']
                    new_min = st.number_input(
                        f"{vital.replace('_', ' ').title()} Min",
                        value=current_min,
                        key=f"threshold_min_{vital}"
                    )
                    self.critical_thresholds[vital]['min'] = new_min
        
        with col2:
            st.write("**Upper Limits (Critical Maximums)**")
            for vital in ['heart_rate', 'temperature', 'oxygen_saturation', 'respiratory_rate']:
                if vital in self.critical_thresholds:
                    current_max = self.critical_thresholds[vital]['max']
                    new_max = st.number_input(
                        f"{vital.replace('_', ' ').title()} Max",
                        value=current_max,
                        key=f"threshold_max_{vital}"
                    )
                    self.critical_thresholds[vital]['max'] = new_max
        
        # Blood pressure special handling
        st.write("**Blood Pressure Thresholds**")
        bp_col1, bp_col2, bp_col3, bp_col4 = st.columns(4)
        
        with bp_col1:
            self.critical_thresholds['blood_pressure_systolic']['min'] = st.number_input(
                "Systolic Min", 
                value=self.critical_thresholds['blood_pressure_systolic']['min'],
                key="bp_sys_min"
            )
        
        with bp_col2:
            self.critical_thresholds['blood_pressure_systolic']['max'] = st.number_input(
                "Systolic Max", 
                value=self.critical_thresholds['blood_pressure_systolic']['max'],
                key="bp_sys_max"
            )
        
        with bp_col3:
            self.critical_thresholds['blood_pressure_diastolic']['min'] = st.number_input(
                "Diastolic Min", 
                value=self.critical_thresholds['blood_pressure_diastolic']['min'],
                key="bp_dia_min"
            )
        
        with bp_col4:
            self.critical_thresholds['blood_pressure_diastolic']['max'] = st.number_input(
                "Diastolic Max", 
                value=self.critical_thresholds['blood_pressure_diastolic']['max'],
                key="bp_dia_max"
            )
        
        if st.button("💾 Save Thresholds"):
            st.success("Critical thresholds updated!")
            st.rerun()
