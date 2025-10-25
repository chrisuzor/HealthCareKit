"""
Advanced Health Analytics Module
Handles health trends, historical analysis, and predictive insights
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from config import VITAL_RANGES, VITAL_COLORS
import json

class HealthAnalytics:
    """
    Advanced Health Analytics Module
    Handles health trends, historical analysis, and predictive insights
    """
    def __init__(self):
        """
        Initialize the health analytics system
        """
        self.health_data = self._load_health_data()
        self.health_score_history = []
        
    def _load_health_data(self):
        """
        Load historical health data from session state or file
        """
        if 'health_data' not in st.session_state:
            st.session_state.health_data = {
                'heart_rate': [],
                'blood_pressure_systolic': [],
                'blood_pressure_diastolic': [],
                'temperature': [],
                'oxygen_saturation': [],
                'respiratory_rate': [],
                'ecg_value': [],
                'ecg_leads_connected': [],
                'timestamp': [],
                'health_score': []
            }
        else:
            # Backward compatibility: add ECG fields if they don't exist
            if 'ecg_value' not in st.session_state.health_data:
                st.session_state.health_data['ecg_value'] = []
            if 'ecg_leads_connected' not in st.session_state.health_data:
                st.session_state.health_data['ecg_leads_connected'] = []
        return st.session_state.health_data
    
    def add_vital_data(self, vitals):
        """Add new vital data to analytics"""
        timestamp = datetime.now()
        
        for vital_name, value in vitals.items():
            if vital_name in self.health_data:
                self.health_data[vital_name].append(value)
        
        if 'ecg_value' not in vitals and 'ecg_value' in self.health_data:
            self.health_data['ecg_value'].append(0)
        if 'ecg_leads_connected' not in vitals and 'ecg_leads_connected' in self.health_data:
            self.health_data['ecg_leads_connected'].append(False)
        
        self.health_data['timestamp'].append(timestamp)
        health_score = self._calculate_health_score(vitals)
        self.health_data['health_score'].append(health_score)
        self._trim_data_history()
    
    def _calculate_health_score(self, vitals):
        """Calculate overall health score based on vital signs"""
        score = 100
        
        hr = vitals.get('heart_rate', 0)
        hr_min, hr_max = VITAL_RANGES['heart_rate']
        if hr < hr_min or hr > hr_max:
            score -= 15
        
        sys_bp = vitals.get('blood_pressure_systolic', 0)
        dia_bp = vitals.get('blood_pressure_diastolic', 0)
        sys_min, sys_max = VITAL_RANGES['blood_pressure_systolic']
        dia_min, dia_max = VITAL_RANGES['blood_pressure_diastolic']
        
        if sys_bp < sys_min or sys_bp > sys_max:
            score -= 10
        if dia_bp < dia_min or dia_bp > dia_max:
            score -= 10
        
        temp = vitals.get('temperature', 0)
        temp_min, temp_max = VITAL_RANGES['temperature']
        if temp < temp_min or temp > temp_max:
            score -= 20
        
        spo2 = vitals.get('oxygen_saturation', 0)
        spo2_min, spo2_max = VITAL_RANGES['oxygen_saturation']
        if spo2 < spo2_min:
            score -= 25
        
        rr = vitals.get('respiratory_rate', 0)
        rr_min, rr_max = VITAL_RANGES['respiratory_rate']
        if rr < rr_min or rr > rr_max:
            score -= 10
        
        return max(0, min(100, score))
    
    def _trim_data_history(self):
        """Keep only recent data points"""
        max_points = 1000
        if len(self.health_data['timestamp']) > max_points:
            for key in self.health_data:
                self.health_data[key] = self.health_data[key][-max_points:]
    
    def _create_dataframe_from_health_data(self):
        if not self.health_data or len(self.health_data.get('timestamp', [])) == 0:
            return pd.DataFrame()
        
        max_len = max(len(v) for v in self.health_data.values() if isinstance(v, list))
        data_for_df = {}
        
        for key, value in self.health_data.items():
            if isinstance(value, list):
                if len(value) < max_len:
                    if key == 'ecg_value':
                        value = value + [0] * (max_len - len(value))
                    elif key == 'ecg_leads_connected':
                        value = value + [False] * (max_len - len(value))
                    else:
                        value = value + [None] * (max_len - len(value))
                data_for_df[key] = value[:max_len]
        
        return pd.DataFrame(data_for_df)
    
    def create_trend_charts(self):
        """Create comprehensive trend analysis charts"""
        if len(self.health_data['timestamp']) < 2:
            st.info("📊 Collect more data to see trends")
            return
        
        max_len = max(len(v) for v in self.health_data.values() if isinstance(v, list))
        data_for_df = {}
        for key, value in self.health_data.items():
            if isinstance(value, list):
                # Pad shorter arrays with appropriate default values
                if len(value) < max_len:
                    if key == 'ecg_value':
                        value = value + [0] * (max_len - len(value))
                    elif key == 'ecg_leads_connected':
                        value = value + [False] * (max_len - len(value))
                    else:
                        value = value + [None] * (max_len - len(value))
                data_for_df[key] = value[:max_len]  # Ensure exact length
        
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(data_for_df)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Create tabs for different time periods
        tab1, tab2, tab3 = st.tabs(["📈 Last 24 Hours", "📊 Last 7 Days", "📅 Last 30 Days"])
        
        with tab1:
            self._create_time_period_chart(df, hours=24)
        
        with tab2:
            self._create_time_period_chart(df, days=7)
        
        with tab3:
            self._create_time_period_chart(df, days=30)
    
    def _create_time_period_chart(self, df, hours=None, days=None):
        """Create charts for specific time periods"""
        if hours:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            key_suffix = f"{hours}h"
        elif days:
            cutoff_time = datetime.now() - timedelta(days=days)
            key_suffix = f"{days}d"
        else:
            key_suffix = "all"
        period_df = df[df['timestamp'] >= cutoff_time]
        
        if len(period_df) < 2:
            st.info(f"Not enough data for this time period")
            return
        
        # Create subplots for all vitals
        fig = go.Figure()
        
        # Add traces for each vital
        vitals_to_plot = ['heart_rate', 'temperature', 'oxygen_saturation', 'respiratory_rate']
        colors = ['#FF6B6B', '#1e938b', '#96CEB4', '#FFEAA7']
        
        for i, vital in enumerate(vitals_to_plot):
            if vital in period_df.columns and not period_df[vital].isna().all():
                fig.add_trace(go.Scatter(
                    x=period_df['timestamp'],
                    y=period_df[vital],
                    mode='lines+markers',
                    name=vital.replace('_', ' ').title(),
                    line=dict(color=colors[i], width=2),
                    marker=dict(size=4)
                ))
        
        fig.update_layout(
            title=f"Vital Signs Trends ({hours}h ago)" if hours else f"Vital Signs Trends ({days} days ago)",
            xaxis_title="Time",
            yaxis_title="Value",
            height=400,
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True, key=f"vital_trend_{key_suffix}")
        
        # Health score trend
        if 'health_score' in period_df.columns:
            self._create_health_score_chart(period_df, key_suffix=key_suffix)
    
    def _create_health_score_chart(self, df, key_suffix=""):
        """Create health score trend chart"""
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['health_score'],
            mode='lines+markers',
            name='Health Score',
            line=dict(color='#28a745', width=3),
            marker=dict(size=6)
        ))
        
        # Add horizontal lines for score ranges
        fig.add_hline(y=80, line_dash="dash", line_color="green", annotation_text="Good Health")
        fig.add_hline(y=60, line_dash="dash", line_color="orange", annotation_text="Fair Health")
        fig.add_hline(y=40, line_dash="dash", line_color="red", annotation_text="Poor Health")
        
        fig.update_layout(
            title="Health Score Trend",
            xaxis_title="Time",
            yaxis_title="Health Score (0-100)",
            height=300,
            yaxis=dict(range=[0, 100])
        )
        
        st.plotly_chart(fig, use_container_width=True, key=f"health_trend_score_{key_suffix}")
    
    def create_correlation_analysis(self):
        """Create correlation analysis between vital signs"""
        if len(self.health_data['timestamp']) < 10:
            st.info("📊 Need at least 10 data points for correlation analysis")
            return
        
        # Ensure all arrays have the same length before creating DataFrame
        max_len = max(len(v) for v in self.health_data.values() if isinstance(v, list))
        data_for_df = {}
        for key, value in self.health_data.items():
            if isinstance(value, list):
                if len(value) < max_len:
                    if key == 'ecg_value':
                        value = value + [0] * (max_len - len(value))
                    elif key == 'ecg_leads_connected':
                        value = value + [False] * (max_len - len(value))
                    else:
                        value = value + [None] * (max_len - len(value))
                data_for_df[key] = value[:max_len]
        
        df = pd.DataFrame(data_for_df)
        
        # Select numeric columns for correlation
        numeric_cols = ['heart_rate', 'blood_pressure_systolic', 'blood_pressure_diastolic', 
                       'temperature', 'oxygen_saturation', 'respiratory_rate']
        
        # Filter columns that exist and have data
        available_cols = [col for col in numeric_cols if col in df.columns and not df[col].isna().all()]
        
        if len(available_cols) < 2:
            st.info("Not enough data for correlation analysis")
            return
        
        # Calculate correlation matrix
        corr_matrix = df[available_cols].corr()
        
        # Create heatmap
        fig = px.imshow(
            corr_matrix,
            text_auto=True,
            aspect="auto",
            color_continuous_scale="RdBu",
            title="Vital Signs Correlation Matrix"
        )
        
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Show insights
        self._analyze_correlations(corr_matrix)
    
    def _analyze_correlations(self, corr_matrix):
        """Analyze and display correlation insights"""
        st.subheader("🔍 Correlation Insights")
        
        # Find strongest correlations
        correlations = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]
                if abs(corr_value) > 0.3:  # Only show significant correlations
                    correlations.append({
                        'vital1': corr_matrix.columns[i],
                        'vital2': corr_matrix.columns[j],
                        'correlation': corr_value
                    })
        
        if correlations:
            for corr in sorted(correlations, key=lambda x: abs(x['correlation']), reverse=True):
                strength = "Strong" if abs(corr['correlation']) > 0.7 else "Moderate"
                direction = "positive" if corr['correlation'] > 0 else "negative"
                
                st.info(f"**{strength} {direction} correlation** between {corr['vital1'].replace('_', ' ')} and {corr['vital2'].replace('_', ' ')} ({corr['correlation']:.2f})")
        else:
            st.info("No significant correlations found in current data")
    
    def create_health_summary(self):
        """Create comprehensive health summary"""
        if len(self.health_data['timestamp']) == 0:
            st.info("No health data available yet")
            return
        
        # Ensure all arrays have the same length before creating DataFrame
        max_len = max(len(v) for v in self.health_data.values() if isinstance(v, list))
        data_for_df = {}
        for key, value in self.health_data.items():
            if isinstance(value, list):
                # Pad shorter arrays with None or appropriate default values
                if len(value) < max_len:
                    if key == 'ecg_value':
                        value = value + [0] * (max_len - len(value))
                    elif key == 'ecg_leads_connected':
                        value = value + [False] * (max_len - len(value))
                    elif key == 'timestamp':
                        continue  # Skip if timestamp array is short
                    else:
                        value = value + [None] * (max_len - len(value))
                data_for_df[key] = value[:max_len]  # Ensure exact length
        
        df = pd.DataFrame(data_for_df)
        
        # Calculate statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_health_score = df['health_score'].mean() if 'health_score' in df.columns else 0
            st.metric("Average Health Score", f"{avg_health_score:.1f}/100")
        
        with col2:
            data_points = len(df)
            st.metric("Data Points Collected", f"{data_points}")
        
        with col3:
            if len(df) > 1:
                trend = df['health_score'].iloc[-1] - df['health_score'].iloc[0] if 'health_score' in df.columns else 0
                st.metric("Health Trend", f"{trend:+.1f}", delta=f"{trend:+.1f}")
        
        with col4:
            latest_score = df['health_score'].iloc[-1] if 'health_score' in df.columns else 0
            if latest_score >= 80:
                status = "🟢 Excellent"
            elif latest_score >= 60:
                status = "🟡 Good"
            else:
                status = "🔴 Needs Attention"
            st.metric("Current Status", status)
        
        # Show recent vital averages
        st.subheader("📊 Recent Vital Averages")
        recent_data = df.tail(10)  # Last 10 readings
        
        vital_cols = ['heart_rate', 'temperature', 'oxygen_saturation', 'respiratory_rate']
        cols = st.columns(len(vital_cols))
        
        for i, vital in enumerate(vital_cols):
            if vital in recent_data.columns:
                avg_value = recent_data[vital].mean()
                unit = "BPM" if vital == "heart_rate" else "°C" if vital == "temperature" else "%" if vital == "oxygen_saturation" else "breaths/min"
                with cols[i]:
                    st.metric(vital.replace('_', ' ').title(), f"{avg_value:.1f} {unit}")
    
    def export_health_data(self):
        """Export health data to CSV"""
        if len(self.health_data['timestamp']) == 0:
            st.warning("No data to export")
            return
        
        # Ensure all arrays have the same length before creating DataFrame
        max_len = max(len(v) for v in self.health_data.values() if isinstance(v, list))
        data_for_df = {}
        for key, value in self.health_data.items():
            if isinstance(value, list):
                if len(value) < max_len:
                    if key == 'ecg_value':
                        value = value + [0] * (max_len - len(value))
                    elif key == 'ecg_leads_connected':
                        value = value + [False] * (max_len - len(value))
                    else:
                        value = value + [None] * (max_len - len(value))
                data_for_df[key] = value[:max_len]
        
        df = pd.DataFrame(data_for_df)
        
        # Create comprehensive report
        report_data = {
            'summary': {
                'total_readings': len(df),
                'date_range': f"{df['timestamp'].min()} to {df['timestamp'].max()}",
                'average_health_score': df['health_score'].mean() if 'health_score' in df.columns else 0
            },
            'vital_statistics': {},
            'trends': {}
        }
        
        # Calculate vital statistics
        for vital in ['heart_rate', 'temperature', 'oxygen_saturation', 'respiratory_rate']:
            if vital in df.columns:
                report_data['vital_statistics'][vital] = {
                    'mean': df[vital].mean(),
                    'std': df[vital].std(),
                    'min': df[vital].min(),
                    'max': df[vital].max()
                }
        
        # Export options
        col1, col2 = st.columns(2)
        
        with col1:
            # CSV export
            csv_data = df.to_csv(index=False)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"health_report_{timestamp}.csv"
            
            st.download_button(
                label="📊 Download CSV Report",
                data=csv_data,
                file_name=filename,
                mime="text/csv"
            )
        
        with col2:
            # JSON export
            json_data = json.dumps(report_data, indent=2, default=str)
            json_filename = f"health_summary_{timestamp}.json"
            
            st.download_button(
                label="📋 Download JSON Summary",
                data=json_data,
                file_name=json_filename,
                mime="application/json"
            )
