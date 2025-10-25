"""
Smart Notifications & Reminders Module
Handles medication reminders, health check-ups, and custom notifications
"""

import streamlit as st
import json
from datetime import datetime, timedelta, time
import threading
import time as time_module

class NotificationSystem:
    def __init__(self):
        """Initialize notification system"""
        self.reminders = self._load_reminders()
        self.notification_settings = self._load_notification_settings()
        self.notification_history = self._load_notification_history()
        
    def _load_reminders(self):
        """Load reminder data"""
        if 'reminders' not in st.session_state:
            st.session_state.reminders = []
        return st.session_state.reminders
    
    def _load_notification_settings(self):
        """Load notification settings"""
        if 'notification_settings' not in st.session_state:
            st.session_state.notification_settings = {
                'medication_reminders': True,
                'health_check_reminders': True,
                'exercise_reminders': True,
                'hydration_reminders': True,
                'appointment_reminders': True,
                'notification_sound': True,
                'notification_frequency': 'normal',  # low, normal, high
                'quiet_hours_start': '22:00',
                'quiet_hours_end': '07:00'
            }
        return st.session_state.notification_settings
    
    def _load_notification_history(self):
        """Load notification history"""
        if 'notification_history' not in st.session_state:
            st.session_state.notification_history = []
        return st.session_state.notification_history
    
    def create_notifications_dashboard(self):
        """Create notifications dashboard"""
        st.subheader("🔔 Smart Notifications & Reminders")
        
        # Notification overview
        self._show_notification_overview()
        
        # Notification tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "⏰ Reminders", 
            "💊 Medication Alerts", 
            "⚙️ Settings", 
            "📋 History"
        ])
        
        with tab1:
            self._create_reminders_tab()
        
        with tab2:
            self._create_medication_alerts_tab()
        
        with tab3:
            self._create_settings_tab()
        
        with tab4:
            self._create_history_tab()
    
    def _show_notification_overview(self):
        """Show notification overview"""
        active_reminders = len([r for r in self.reminders if r['active']])
        today_reminders = len([r for r in self.reminders if self._is_reminder_today(r)])
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Active Reminders", active_reminders)
        
        with col2:
            st.metric("Today's Reminders", today_reminders)
        
        with col3:
            notifications_enabled = sum([
                self.notification_settings['medication_reminders'],
                self.notification_settings['health_check_reminders'],
                self.notification_settings['exercise_reminders'],
                self.notification_settings['hydration_reminders'],
                self.notification_settings['appointment_reminders']
            ])
            st.metric("Notification Types", f"{notifications_enabled}/5")
        
        with col4:
            recent_notifications = len([n for n in self.notification_history if (datetime.now() - datetime.strptime(n['timestamp'], '%Y-%m-%d %H:%M:%S')).days < 1])
            st.metric("Notifications Today", recent_notifications)
    
    def _create_reminders_tab(self):
        """Create reminders management tab"""
        st.subheader("⏰ Health Reminders")
        
        # Add new reminder
        with st.expander("➕ Add New Reminder", expanded=False):
            with st.form("add_reminder"):
                col1, col2 = st.columns(2)
                
                with col1:
                    reminder_type = st.selectbox("Reminder Type", [
                        "Medication",
                        "Health Check",
                        "Exercise",
                        "Hydration",
                        "Appointment",
                        "Custom"
                    ])
                    reminder_title = st.text_input("Reminder Title")
                    reminder_time = st.time_input("Reminder Time")
                
                with col2:
                    frequency = st.selectbox("Frequency", [
                        "Once",
                        "Daily",
                        "Weekly",
                        "Monthly"
                    ])
                    priority = st.selectbox("Priority", ["Low", "Medium", "High"])
                    description = st.text_area("Description")
                
                if st.form_submit_button("Add Reminder"):
                    new_reminder = {
                        'id': len(self.reminders) + 1,
                        'type': reminder_type,
                        'title': reminder_title,
                        'time': reminder_time.strftime('%H:%M'),
                        'frequency': frequency,
                        'priority': priority,
                        'description': description,
                        'active': True,
                        'created_date': datetime.now().strftime('%Y-%m-%d'),
                        'last_triggered': None,
                        'next_trigger': self._calculate_next_trigger(reminder_time, frequency)
                    }
                    self.reminders.append(new_reminder)
                    st.success("Reminder added successfully!")
                    st.rerun()
        
        # Display reminders
        if self.reminders:
            st.subheader("📋 Current Reminders")
            
            # Filter options
            col1, col2 = st.columns(2)
            with col1:
                type_filter = st.selectbox("Filter by Type", ["All"] + list(set([r['type'] for r in self.reminders])))
            with col2:
                status_filter = st.selectbox("Filter by Status", ["All", "Active", "Inactive"])
            
            # Filter reminders
            filtered_reminders = self.reminders
            if type_filter != "All":
                filtered_reminders = [r for r in filtered_reminders if r['type'] == type_filter]
            if status_filter != "All":
                active_status = status_filter == "Active"
                filtered_reminders = [r for r in filtered_reminders if r['active'] == active_status]
            
            # Display filtered reminders
            for reminder in filtered_reminders:
                self._display_reminder_card(reminder)
        else:
            st.info("No reminders set yet. Create your first health reminder!")
    
    def _display_reminder_card(self, reminder):
        """Display individual reminder card"""
        priority_colors = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}
        
        with st.expander(f"{priority_colors[reminder['priority']]} {reminder['title']} - {reminder['time']}"):
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"**Type:** {reminder['type']}")
                st.write(f"**Time:** {reminder['time']}")
                st.write(f"**Frequency:** {reminder['frequency']}")
                st.write(f"**Priority:** {reminder['priority']}")
                st.write(f"**Status:** {'Active' if reminder['active'] else 'Inactive'}")
                
                if reminder['description']:
                    st.write(f"**Description:** {reminder['description']}")
                
                if reminder['next_trigger']:
                    st.write(f"**Next Trigger:** {reminder['next_trigger']}")
            
            with col2:
                if reminder['active']:
                    if st.button(" Pause", key=f"pause_{reminder['id']}"):
                        reminder['active'] = False
                        st.success("Reminder paused")
                        st.rerun()
                else:
                    if st.button("▶️ Resume", key=f"resume_{reminder['id']}"):
                        reminder['active'] = True
                        st.success("Reminder resumed")
                        st.rerun()
            
            with col3:
                if st.button("🗑️ Delete", key=f"delete_{reminder['id']}"):
                    self.reminders.remove(reminder)
                    st.success("Reminder deleted")
                    st.rerun()
    
    def _create_medication_alerts_tab(self):
        """Create medication alerts tab"""
        st.subheader("💊 Medication Reminders")
        
        # Auto-generate medication reminders from patient profile
        if 'medications' in st.session_state and st.session_state.medications:
            st.write("**Auto-Generated Medication Reminders**")
            
            active_medications = [m for m in st.session_state.medications if m.get('active', True)]
            
            for med in active_medications:
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.write(f"**{med['name']}** - {med['dosage']}")
                    st.write(f"Frequency: {med['frequency']}")
                
                with col2:
                    if st.button(f"Set Reminder", key=f"med_reminder_{med['name']}"):
                        self._create_medication_reminder(med)
                        st.success("Medication reminder created!")
                
                with col3:
                    # Check if reminder already exists
                    existing_reminder = any(r['title'] == f"Take {med['name']}" for r in self.reminders)
                    if existing_reminder:
                        st.success(" Reminder Set")
                    else:
                        st.info("No Reminder")
        
        # Medication adherence tracking
        st.subheader("📊 Medication Adherence")
        
        if st.button("📈 View Adherence Report"):
            self._show_adherence_report()
    
    def _create_medication_reminder(self, medication):
        """Create medication reminder from medication data"""
        # Parse frequency to determine reminder times
        frequency = medication['frequency'].lower()
        
        reminder_times = []
        if 'once daily' in frequency:
            reminder_times = ['09:00']
        elif 'twice daily' in frequency:
            reminder_times = ['09:00', '21:00']
        elif 'three times daily' in frequency:
            reminder_times = ['08:00', '14:00', '20:00']
        else:
            reminder_times = ['09:00']  # Default
        
        for time_str in reminder_times:
            reminder = {
                'id': len(self.reminders) + 1,
                'type': 'Medication',
                'title': f"Take {medication['name']}",
                'time': time_str,
                'frequency': 'Daily',
                'priority': 'High',
                'description': f"Take {medication['dosage']} of {medication['name']}",
                'active': True,
                'created_date': datetime.now().strftime('%Y-%m-%d'),
                'last_triggered': None,
                'next_trigger': self._calculate_next_trigger(datetime.strptime(time_str, '%H:%M').time(), 'Daily')
            }
            self.reminders.append(reminder)
    
    def _show_adherence_report(self):
        """Show medication adherence report"""
        st.subheader(" Medication Adherence Report")
        
        # This would integrate with actual adherence data
        # For now, show sample data
        
        adherence_data = {
            'Medication 1': {'adherence': 95, 'missed_doses': 2},
            'Medication 2': {'adherence': 88, 'missed_doses': 5},
            'Medication 3': {'adherence': 100, 'missed_doses': 0}
        }
        
        for med_name, data in adherence_data.items():
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**{med_name}**")
            
            with col2:
                st.metric("Adherence Rate", f"{data['adherence']}%")
            
            with col3:
                st.metric("Missed Doses", data['missed_doses'])
    
    def _create_settings_tab(self):
        """Create notification settings tab"""
        st.subheader("⚙️ Notification Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Notification Types**")
            
            self.notification_settings['medication_reminders'] = st.checkbox(
                "Medication Reminders",
                value=self.notification_settings['medication_reminders']
            )
            
            self.notification_settings['health_check_reminders'] = st.checkbox(
                "Health Check Reminders",
                value=self.notification_settings['health_check_reminders']
            )
            
            self.notification_settings['exercise_reminders'] = st.checkbox(
                "Exercise Reminders",
                value=self.notification_settings['exercise_reminders']
            )
            
            self.notification_settings['hydration_reminders'] = st.checkbox(
                "Hydration Reminders",
                value=self.notification_settings['hydration_reminders']
            )
            
            self.notification_settings['appointment_reminders'] = st.checkbox(
                "Appointment Reminders",
                value=self.notification_settings['appointment_reminders']
            )
        
        with col2:
            st.write("**Notification Preferences**")
            
            self.notification_settings['notification_sound'] = st.checkbox(
                "Notification Sound",
                value=self.notification_settings['notification_sound']
            )
            
            freq_options = ["Low", "Normal", "High"]
            current_freq = self.notification_settings['notification_frequency'].capitalize()
            index = freq_options.index(current_freq) if current_freq in freq_options else 1  # Default to 'Normal'
            self.notification_settings['notification_frequency'] = st.selectbox(
                "Notification Frequency",
                freq_options,
                index=index
            )
            
            st.write("**Quiet Hours**")
            
            col2_1, col2_2 = st.columns(2)
            with col2_1:
                self.notification_settings['quiet_hours_start'] = st.time_input(
                    "Start Time",
                    value=datetime.strptime(self.notification_settings['quiet_hours_start'], '%H:%M').time()
                ).strftime('%H:%M')
            
            with col2_2:
                self.notification_settings['quiet_hours_end'] = st.time_input(
                    "End Time",
                    value=datetime.strptime(self.notification_settings['quiet_hours_end'], '%H:%M').time()
                ).strftime('%H:%M')
        
        if st.button("💾 Save Settings"):
            st.success("Notification settings saved!")
    
    def _create_history_tab(self):
        """Create notification history tab"""
        st.subheader("📋 Notification History")
        
        if self.notification_history:
            # Filter options
            col1, col2 = st.columns(2)
            with col1:
                days_filter = st.selectbox("Show Last", ["1 day", "7 days", "30 days", "All"])
            with col2:
                type_filter = st.selectbox("Filter by Type", ["All"] + list(set([n['type'] for n in self.notification_history])))
            
            # Filter notifications
            filtered_notifications = self.notification_history
            
            if days_filter != "All":
                days = int(days_filter.split()[0])
                cutoff_date = datetime.now() - timedelta(days=days)
                filtered_notifications = [
                    n for n in filtered_notifications 
                    if datetime.strptime(n['timestamp'], '%Y-%m-%d %H:%M:%S') >= cutoff_date
                ]
            
            if type_filter != "All":
                filtered_notifications = [n for n in filtered_notifications if n['type'] == type_filter]
            
            # Display notifications
            for notification in reversed(filtered_notifications[-20:]):  # Show last 20
                timestamp = datetime.strptime(notification['timestamp'], '%Y-%m-%d %H:%M:%S')
                time_ago = datetime.now() - timestamp
                
                if notification['status'] == 'delivered':
                    st.success(f" {notification['message']} ({time_ago.seconds//60} minutes ago)")
                elif notification['status'] == 'missed':
                    st.error(f" {notification['message']} - MISSED ({time_ago.seconds//60} minutes ago)")
                else:
                    st.info(f" {notification['message']} ({time_ago.seconds//60} minutes ago)")
        else:
            st.info("No notification history yet")
    
    def _calculate_next_trigger(self, reminder_time, frequency):
        """Calculate next trigger time for reminder"""
        now = datetime.now()
        reminder_datetime = datetime.combine(now.date(), reminder_time)
        
        if frequency == "Once":
            return reminder_datetime.strftime('%Y-%m-%d %H:%M') if reminder_datetime > now else None
        elif frequency == "Daily":
            if reminder_datetime > now:
                return reminder_datetime.strftime('%Y-%m-%d %H:%M')
            else:
                return (reminder_datetime + timedelta(days=1)).strftime('%Y-%m-%d %H:%M')
        elif frequency == "Weekly":
            next_week = reminder_datetime + timedelta(weeks=1)
            return next_week.strftime('%Y-%m-%d %H:%M')
        elif frequency == "Monthly":
            next_month = reminder_datetime + timedelta(days=30)
            return next_month.strftime('%Y-%m-%d %H:%M')
        
        return None
    
    def _is_reminder_today(self, reminder):
        """Check if reminder should trigger today"""
        if not reminder['active']:
            return False
        
        now = datetime.now()
        reminder_time = datetime.strptime(reminder['time'], '%H:%M').time()
        
        if reminder['frequency'] == "Daily":
            return True
        elif reminder['frequency'] == "Weekly":
            # Check if it's the same day of week as created
            created_date = datetime.strptime(reminder['created_date'], '%Y-%m-%d')
            return now.weekday() == created_date.weekday()
        elif reminder['frequency'] == "Monthly":
            # Check if it's the same day of month
            created_date = datetime.strptime(reminder['created_date'], '%Y-%m-%d')
            return now.day == created_date.day
        
        return False
    
    def check_and_trigger_reminders(self):
        """Check for due reminders and trigger them"""
        now = datetime.now()
        triggered_reminders = []
        
        for reminder in self.reminders:
            if not reminder['active']:
                continue
            
            if self._is_reminder_today(reminder):
                reminder_time = datetime.strptime(reminder['time'], '%H:%M').time()
                current_time = now.time()
                
                # Check if it's time to trigger (within 1 minute)
                time_diff = abs((datetime.combine(now.date(), current_time) - 
                               datetime.combine(now.date(), reminder_time)).total_seconds())
                
                if time_diff <= 60:  # Within 1 minute
                    # Check if not already triggered today
                    last_triggered = reminder.get('last_triggered')
                    if not last_triggered or datetime.strptime(last_triggered, '%Y-%m-%d').date() != now.date():
                        self._trigger_reminder(reminder)
                        triggered_reminders.append(reminder)
        
        return triggered_reminders
    
    def _trigger_reminder(self, reminder):
        """Trigger a reminder notification"""
        notification = {
            'id': len(self.notification_history) + 1,
            'type': reminder['type'],
            'message': f"Reminder: {reminder['title']}",
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'delivered',
            'priority': reminder['priority']
        }
        
        self.notification_history.append(notification)
        reminder['last_triggered'] = datetime.now().strftime('%Y-%m-%d')
        
        # Show notification in Streamlit
        if reminder['priority'] == 'High':
            st.error(f" {reminder['title']} - {reminder['description']}")
        elif reminder['priority'] == 'Medium':
            st.warning(f" {reminder['title']} - {reminder['description']}")
        else:
            st.info(f" {reminder['title']} - {reminder['description']}")
    
    def create_smart_reminders(self, vitals):
        """Create smart reminders based on current vitals"""
        smart_reminders = []
        
        # Blood pressure reminders
        if vitals.get('blood_pressure_systolic', 0) > 140:
            smart_reminders.append({
                'type': 'Health Check',
                'title': 'High Blood Pressure Alert',
                'message': 'Your blood pressure is elevated. Consider relaxation techniques.',
                'priority': 'High'
            })
        
        # Heart rate reminders
        if vitals.get('heart_rate', 0) > 100:
            smart_reminders.append({
                'type': 'Health Check',
                'title': 'Elevated Heart Rate',
                'message': 'Your heart rate is elevated. Consider taking a break.',
                'priority': 'Medium'
            })
        
        # Temperature reminders
        if vitals.get('temperature', 0) > 37.5:
            smart_reminders.append({
                'type': 'Health Check',
                'title': 'Elevated Temperature',
                'message': 'Your temperature is elevated. Stay hydrated and rest.',
                'priority': 'High'
            })
        
        # Add smart reminders to history
        for reminder in smart_reminders:
            notification = {
                'id': len(self.notification_history) + 1,
                'type': reminder['type'],
                'message': reminder['message'],
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'delivered',
                'priority': reminder['priority']
            }
            self.notification_history.append(notification)
        
        return smart_reminders
