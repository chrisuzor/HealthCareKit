"""
Patient Profile & Medical History Module
Handles user profiles, medical history, and medication tracking
"""

import streamlit as st
import json
from datetime import datetime, date
import pandas as pd

class PatientProfile:
    def __init__(self):
        """Initialize patient profile system"""
        self.profile_data = self._load_profile_data()
        self.medical_history = self._load_medical_history()
        self.medications = self._load_medications()
        self.allergies = self._load_allergies()
        
    def _load_profile_data(self):
        """Load patient profile data"""
        if 'patient_profile' not in st.session_state:
            st.session_state.patient_profile = {
                'personal_info': {
                    'first_name': '',
                    'last_name': '',
                    'date_of_birth': None,
                    'gender': '',
                    'height': 0,  # cm
                    'weight': 0,   # kg
                    'blood_type': '',
                    'emergency_contact': '',
                    'phone': '',
                    'email': ''
                },
                'medical_info': {
                    'primary_physician': '',
                    'insurance_provider': '',
                    'policy_number': '',
                    'medical_conditions': [],
                    'family_history': []
                }
            }
        return st.session_state.patient_profile
    
    def _load_medical_history(self):
        """Load medical history"""
        if 'medical_history' not in st.session_state:
            st.session_state.medical_history = []
        return st.session_state.medical_history
    
    def _load_medications(self):
        """Load medication list"""
        if 'medications' not in st.session_state:
            st.session_state.medications = []
        return st.session_state.medications
    
    def _load_allergies(self):
        """Load allergy information"""
        if 'allergies' not in st.session_state:
            st.session_state.allergies = []
        return st.session_state.allergies
    
    def create_profile_dashboard(self):
        """Create patient profile dashboard"""
        st.subheader("👤 Patient Profile")
        
        # Profile overview
        self._show_profile_overview()
        
        # Profile tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📋 Personal Info", 
            "🏥 Medical History", 
            "💊 Medications", 
            "🚫 Allergies", 
            "📊 Health Summary"
        ])
        
        with tab1:
            self._create_personal_info_tab()
        
        with tab2:
            self._create_medical_history_tab()
        
        with tab3:
            self._create_medications_tab()
        
        with tab4:
            self._create_allergies_tab()
        
        with tab5:
            self._create_health_summary_tab()
    
    def _show_profile_overview(self):
        """Show profile overview cards"""
        personal = self.profile_data['personal_info']
        medical = self.profile_data['medical_info']
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            name = f"{personal['first_name']} {personal['last_name']}" if personal['first_name'] else "Not Set"
            st.metric("Patient Name", name)
        
        with col2:
            age = self._calculate_age(personal['date_of_birth']) if personal['date_of_birth'] else "Not Set"
            st.metric("Age", f"{age} years" if isinstance(age, int) else age)
        
        with col3:
            bmi = self._calculate_bmi(personal['height'], personal['weight'])
            st.metric("BMI", f"{bmi:.1f}" if bmi else "Not Set")
        
        with col4:
            med_count = len(self.medications)
            st.metric("Active Medications", med_count)
    
    def _calculate_age(self, birth_date):
        """Calculate age from birth date"""
        if not birth_date:
            return None
        
        if isinstance(birth_date, str):
            birth_date = datetime.strptime(birth_date, '%Y-%m-%d').date()
        
        today = date.today()
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    
    def _calculate_bmi(self, height, weight):
        """Calculate BMI"""
        if height > 0 and weight > 0:
            height_m = height / 100  # Convert cm to meters
            return weight / (height_m ** 2)
        return None
    
    def _create_personal_info_tab(self):
        """Create personal information tab"""
        st.subheader("📋 Personal Information")
        
        personal = self.profile_data['personal_info']
        
        col1, col2 = st.columns(2)
        
        with col1:
            personal['first_name'] = st.text_input("First Name", value=personal['first_name'])
            personal['last_name'] = st.text_input("Last Name", value=personal['last_name'])
            personal['date_of_birth'] = st.date_input("Date of Birth", value=personal['date_of_birth'])
            personal['gender'] = st.selectbox("Gender", ["", "Male", "Female", "Other"], index=["", "Male", "Female", "Other"].index(personal['gender']) if personal['gender'] else 0)
            personal['height'] = st.number_input("Height (cm)", value=personal['height'], min_value=0, max_value=300)
        
        with col2:
            personal['weight'] = st.number_input("Weight (kg)", value=float(personal['weight']), min_value=0.0, max_value=500.0)
            personal['blood_type'] = st.selectbox("Blood Type", ["", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"], index=["", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"].index(personal['blood_type']) if personal['blood_type'] else 0)
            personal['phone'] = st.text_input("Phone Number", value=personal['phone'])
            personal['email'] = st.text_input("Email", value=personal['email'])
            personal['emergency_contact'] = st.text_input("Emergency Contact", value=personal['emergency_contact'])
        
        # Medical provider info
        st.subheader("🏥 Medical Provider Information")
        medical = self.profile_data['medical_info']
        
        med_col1, med_col2 = st.columns(2)
        
        with med_col1:
            medical['primary_physician'] = st.text_input("Primary Physician", value=medical['primary_physician'])
            medical['insurance_provider'] = st.text_input("Insurance Provider", value=medical['insurance_provider'])
        
        with med_col2:
            medical['policy_number'] = st.text_input("Policy Number", value=medical['policy_number'])
        
        if st.button("💾 Save Profile"):
            st.success("Profile saved successfully!")
    
    def _create_medical_history_tab(self):
        """Create medical history tab"""
        st.subheader("🏥 Medical History")
        
        # Add new medical event
        with st.expander("➕ Add Medical Event", expanded=False):
            with st.form("add_medical_event"):
                col1, col2 = st.columns(2)
                
                with col1:
                    event_type = st.selectbox("Event Type", ["Diagnosis", "Procedure", "Hospitalization", "Test Result", "Other"])
                    event_date = st.date_input("Event Date")
                    condition = st.text_input("Condition/Procedure")
                
                with col2:
                    doctor = st.text_input("Doctor/Provider")
                    notes = st.text_area("Notes")
                
                if st.form_submit_button("Add Event"):
                    new_event = {
                        'type': event_type,
                        'date': event_date.strftime('%Y-%m-%d'),
                        'condition': condition,
                        'doctor': doctor,
                        'notes': notes,
                        'added_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    self.medical_history.append(new_event)
                    st.success("Medical event added!")
                    st.rerun()
        
        # Display medical history
        if self.medical_history:
            st.subheader("📋 Medical History Timeline")
            
            # Sort by date (most recent first)
            sorted_history = sorted(self.medical_history, key=lambda x: x['date'], reverse=True)
            
            for event in sorted_history:
                with st.expander(f"{event['type']}: {event['condition']} ({event['date']})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Date:** {event['date']}")
                        st.write(f"**Type:** {event['type']}")
                        st.write(f"**Condition:** {event['condition']}")
                    
                    with col2:
                        st.write(f"**Doctor:** {event['doctor']}")
                        st.write(f"**Added:** {event['added_date']}")
                    
                    if event['notes']:
                        st.write(f"**Notes:** {event['notes']}")
        else:
            st.info("No medical history recorded yet")
    
    def _create_medications_tab(self):
        """Create medications tab"""
        st.subheader("💊 Medication Management")
        
        # Add new medication
        with st.expander("➕ Add Medication", expanded=False):
            with st.form("add_medication"):
                col1, col2 = st.columns(2)
                
                with col1:
                    medication_name = st.text_input("Medication Name")
                    dosage = st.text_input("Dosage")
                    frequency = st.selectbox("Frequency", ["Once daily", "Twice daily", "Three times daily", "As needed", "Other"])
                
                with col2:
                    start_date = st.date_input("Start Date")
                    prescribing_doctor = st.text_input("Prescribing Doctor")
                    notes = st.text_area("Notes")
                
                if st.form_submit_button("Add Medication"):
                    new_medication = {
                        'name': medication_name,
                        'dosage': dosage,
                        'frequency': frequency,
                        'start_date': start_date.strftime('%Y-%m-%d'),
                        'doctor': prescribing_doctor,
                        'notes': notes,
                        'active': True,
                        'added_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    self.medications.append(new_medication)
                    st.success("Medication added!")
                    st.rerun()
        
        # Display medications
        if self.medications:
            st.subheader("💊 Current Medications")
            
            active_meds = [med for med in self.medications if med['active']]
            
            if active_meds:
                for i, med in enumerate(active_meds):
                    with st.expander(f"{med['name']} - {med['dosage']}"):
                        col1, col2, col3 = st.columns([2, 1, 1])
                        
                        with col1:
                            st.write(f"**Dosage:** {med['dosage']}")
                            st.write(f"**Frequency:** {med['frequency']}")
                            st.write(f"**Start Date:** {med['start_date']}")
                            st.write(f"**Doctor:** {med['doctor']}")
                            if med['notes']:
                                st.write(f"**Notes:** {med['notes']}")
                        
                        with col2:
                            if st.button(f"Stop Medication", key=f"stop_{i}"):
                                med['active'] = False
                                st.success("Medication marked as inactive")
                                st.rerun()
                        
                        with col3:
                            if st.button(f"Edit", key=f"edit_{i}"):
                                st.info("Edit functionality coming soon!")
            else:
                st.info("No active medications")
        else:
            st.info("No medications recorded yet")
    
    def _create_allergies_tab(self):
        """Create allergies tab"""
        st.subheader("🚫 Allergy Management")
        
        # Add new allergy
        with st.expander("➕ Add Allergy", expanded=False):
            with st.form("add_allergy"):
                col1, col2 = st.columns(2)
                
                with col1:
                    allergen = st.text_input("Allergen")
                    reaction_type = st.selectbox("Reaction Type", ["Mild", "Moderate", "Severe", "Life-threatening"])
                
                with col2:
                    symptoms = st.text_area("Symptoms")
                    notes = st.text_area("Additional Notes")
                
                if st.form_submit_button("Add Allergy"):
                    new_allergy = {
                        'allergen': allergen,
                        'reaction_type': reaction_type,
                        'symptoms': symptoms,
                        'notes': notes,
                        'added_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    self.allergies.append(new_allergy)
                    st.success("Allergy added!")
                    st.rerun()
        
        # Display allergies
        if self.allergies:
            st.subheader("🚫 Known Allergies")
            
            for i, allergy in enumerate(self.allergies):
                severity_color = {
                    'Mild': '🟢',
                    'Moderate': '🟡', 
                    'Severe': '🟠',
                    'Life-threatening': '🔴'
                }
                
                with st.expander(f"{severity_color[allergy['reaction_type']]} {allergy['allergen']} - {allergy['reaction_type']}"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**Reaction Type:** {allergy['reaction_type']}")
                        st.write(f"**Symptoms:** {allergy['symptoms']}")
                        if allergy['notes']:
                            st.write(f"**Notes:** {allergy['notes']}")
                        st.write(f"**Added:** {allergy['added_date']}")
                    
                    with col2:
                        if st.button(f"Remove", key=f"remove_allergy_{i}"):
                            self.allergies.pop(i)
                            st.success("Allergy removed")
                            st.rerun()
        else:
            st.info("No allergies recorded yet")
    
    def _create_health_summary_tab(self):
        """Create health summary tab"""
        st.subheader("📊 Health Summary")
        
        # Calculate health metrics
        personal = self.profile_data['personal_info']
        age = self._calculate_age(personal['date_of_birth'])
        bmi = self._calculate_bmi(personal['height'], personal['weight'])
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Personal Information**")
            st.write(f"• Age: {age} years" if age else "• Age: Not specified")
            st.write(f"• BMI: {bmi:.1f}" if bmi else "• BMI: Not calculated")
            st.write(f"• Blood Type: {personal['blood_type']}" if personal['blood_type'] else "• Blood Type: Not specified")
            
            # BMI interpretation
            if bmi:
                if bmi < 18.5:
                    bmi_status = "Underweight"
                elif bmi < 25:
                    bmi_status = "Normal weight"
                elif bmi < 30:
                    bmi_status = "Overweight"
                else:
                    bmi_status = "Obese"
                st.write(f"• BMI Status: {bmi_status}")
        
        with col2:
            st.write("**Medical Summary**")
            st.write(f"• Active Medications: {len([m for m in self.medications if m['active']])}")
            st.write(f"• Known Allergies: {len(self.allergies)}")
            st.write(f"• Medical Events: {len(self.medical_history)}")
            
            # Risk factors
            risk_factors = []
            if bmi and bmi > 30:
                risk_factors.append("Obesity")
            if len(self.allergies) > 0:
                severe_allergies = len([a for a in self.allergies if a['reaction_type'] in ['Severe', 'Life-threatening']])
                if severe_allergies > 0:
                    risk_factors.append(f"{severe_allergies} severe allergies")
            
            if risk_factors:
                st.write("• Risk Factors:")
                for risk in risk_factors:
                    st.write(f"  - {risk}")
            else:
                st.write("• Risk Factors: None identified")
        
        # Export profile
        st.subheader(" Export Profile")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📋 Export Medical Summary"):
                summary = self._generate_medical_summary()
                st.download_button(
                    label="Download Summary",
                    data=json.dumps(summary, indent=2),
                    file_name=f"medical_summary_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json"
                )
        
        with col2:
            if st.button("📊 Export Full Profile"):
                full_profile = {
                    'profile': self.profile_data,
                    'medical_history': self.medical_history,
                    'medications': self.medications,
                    'allergies': self.allergies
                }
                st.download_button(
                    label="Download Full Profile",
                    data=json.dumps(full_profile, indent=2, default=str),
                    file_name=f"full_profile_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json"
                )
    
    def _generate_medical_summary(self):
        """Generate medical summary for export"""
        personal = self.profile_data['personal_info']
        medical = self.profile_data['medical_info']
        
        return {
            'patient_info': {
                'name': f"{personal['first_name']} {personal['last_name']}",
                'age': self._calculate_age(personal['date_of_birth']),
                'blood_type': personal['blood_type'],
                'bmi': self._calculate_bmi(personal['height'], personal['weight'])
            },
            'medical_summary': {
                'active_medications': len([m for m in self.medications if m['active']]),
                'known_allergies': len(self.allergies),
                'medical_events': len(self.medical_history),
                'primary_physician': medical['primary_physician']
            },
            'medications': [m for m in self.medications if m['active']],
            'allergies': self.allergies,
            'recent_medical_events': self.medical_history[-5:] if self.medical_history else []
        }
    
    def check_medication_interactions(self, vitals):
        """Check for potential medication interactions (placeholder)"""
        # This would integrate with a drug interaction database
        # For now, return basic warnings
        warnings = []
        
        active_meds = [m for m in self.medications if m['active']]
        
        if len(active_meds) > 5:
            warnings.append("⚠️ Multiple medications detected - consult pharmacist for interactions")
        
        # Check for blood pressure medications and current BP
        bp_meds = [m for m in active_meds if 'blood pressure' in m['name'].lower() or 'ace' in m['name'].lower()]
        if bp_meds and vitals.get('blood_pressure_systolic', 0) > 160:
            warnings.append("⚠️ High blood pressure detected with BP medication - contact doctor")
        
        return warnings
