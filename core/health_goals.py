"""
Health Goals & Tracking Module
Handles personal health goals, progress tracking, and achievements
"""

import streamlit as st
import json
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go
from config import VITAL_RANGES

class HealthGoalsTracker:
    def __init__(self):
        """Initialize health goals tracking system"""
        self.goals = self._load_goals()
        self.achievements = self._load_achievements()
        self.progress_data = self._load_progress_data()
        
    def _load_goals(self):
        """Load health goals"""
        if 'health_goals' not in st.session_state:
            st.session_state.health_goals = []
        return st.session_state.health_goals
    
    def _load_achievements(self):
        """Load achievements"""
        if 'achievements' not in st.session_state:
            st.session_state.achievements = []
        return st.session_state.achievements
    
    def _load_progress_data(self):
        """Load progress tracking data"""
        if 'progress_data' not in st.session_state:
            st.session_state.progress_data = {
                'daily_goals': {},
                'weekly_summaries': [],
                'streak_data': {}
            }
        return st.session_state.progress_data
    
    def create_goals_dashboard(self):
        """Create health goals dashboard"""
        st.subheader("🎯 Health Goals & Tracking")
        
        # Goals overview
        self._show_goals_overview()
        
        # Goals tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            " My Goals", 
            " Progress Tracking", 
            " Achievements", 
            " Analytics"
        ])
        
        with tab1:
            self._create_goals_tab()
        
        with tab2:
            self._create_progress_tab()
        
        with tab3:
            self._create_achievements_tab()
        
        with tab4:
            self._create_analytics_tab()
    
    def _show_goals_overview(self):
        """Show goals overview cards"""
        active_goals = [g for g in self.goals if g['status'] == 'active']
        completed_goals = [g for g in self.goals if g['status'] == 'completed']
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Active Goals", len(active_goals))
        
        with col2:
            st.metric("Completed Goals", len(completed_goals))
        
        with col3:
            total_achievements = len(self.achievements)
            st.metric("Achievements", total_achievements)
        
        with col4:
            # Calculate current streak
            current_streak = self._calculate_current_streak()
            st.metric("Current Streak", f"{current_streak} days")
    
    def _create_goals_tab(self):
        """Create goals management tab"""
        st.subheader("🎯 My Health Goals")
        
        # Add new goal
        with st.expander("➕ Add New Goal", expanded=False):
            with st.form("add_goal"):
                col1, col2 = st.columns(2)
                
                with col1:
                    goal_type = st.selectbox("Goal Type", [
                        "Heart Rate Target",
                        "Blood Pressure Control", 
                        "Weight Management",
                        "Exercise Frequency",
                        "Medication Adherence",
                        "Sleep Quality",
                        "Stress Management",
                        "Custom Goal"
                    ])
                    goal_title = st.text_input("Goal Title")
                    target_value = st.number_input("Target Value", min_value=0.0)
                
                with col2:
                    target_unit = st.text_input("Unit (e.g., BPM, mmHg, kg)")
                    target_date = st.date_input("Target Date")
                    priority = st.selectbox("Priority", ["Low", "Medium", "High"])
                
                description = st.text_area("Description")
                
                if st.form_submit_button("Add Goal"):
                    new_goal = {
                        'id': len(self.goals) + 1,
                        'type': goal_type,
                        'title': goal_title,
                        'target_value': target_value,
                        'target_unit': target_unit,
                        'target_date': target_date.strftime('%Y-%m-%d'),
                        'priority': priority,
                        'description': description,
                        'status': 'active',
                        'created_date': datetime.now().strftime('%Y-%m-%d'),
                        'progress': 0,
                        'current_value': 0
                    }
                    self.goals.append(new_goal)
                    st.success("Goal added successfully!")
                    st.rerun()
        
        # Display goals
        if self.goals:
            st.subheader("📋 Current Goals")
            
            # Filter options
            col1, col2, col3 = st.columns(3)
            with col1:
                status_filter = st.selectbox("Filter by Status", ["All", "Active", "Completed", "Paused"])
            with col2:
                priority_filter = st.selectbox("Filter by Priority", ["All", "High", "Medium", "Low"])
            with col3:
                type_filter = st.selectbox("Filter by Type", ["All"] + list(set([g['type'] for g in self.goals])))
            
            # Filter goals
            filtered_goals = self.goals
            if status_filter != "All":
                filtered_goals = [g for g in filtered_goals if g['status'].lower() == status_filter.lower()]
            if priority_filter != "All":
                filtered_goals = [g for g in filtered_goals if g['priority'].lower() == priority_filter.lower()]
            if type_filter != "All":
                filtered_goals = [g for g in filtered_goals if g['type'] == type_filter]
            
            # Display filtered goals
            for goal in filtered_goals:
                self._display_goal_card(goal)
        else:
            st.info("No goals set yet. Create your first health goal!")
    
    def _display_goal_card(self, goal):
        """Display individual goal card"""
        with st.expander(f"{goal['title']} ({goal['priority']} Priority)"):
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"**Type:** {goal['type']}")
                st.write(f"**Target:** {goal['target_value']} {goal['target_unit']}")
                st.write(f"**Target Date:** {goal['target_date']}")
                st.write(f"**Status:** {goal['status'].title()}")
                
                # Progress bar
                progress = goal['progress']
                st.progress(progress / 100)
                st.write(f"Progress: {progress:.1f}%")
                
                if goal['description']:
                    st.write(f"**Description:** {goal['description']}")
            
            with col2:
                if goal['status'] == 'active':
                    if st.button("✅ Complete", key=f"complete_{goal['id']}"):
                        goal['status'] = 'completed'
                        goal['completed_date'] = datetime.now().strftime('%Y-%m-%d')
                        self._award_achievement("goal_completed", goal)
                        st.success("Goal completed!")
                        st.rerun()
                    
                    if st.button("⏸️ Pause", key=f"pause_{goal['id']}"):
                        goal['status'] = 'paused'
                        st.success("Goal paused")
                        st.rerun()
                
                elif goal['status'] == 'paused':
                    if st.button("▶️ Resume", key=f"resume_{goal['id']}"):
                        goal['status'] = 'active'
                        st.success("Goal resumed")
                        st.rerun()
            
            with col3:
                if st.button("🗑️ Delete", key=f"delete_{goal['id']}"):
                    self.goals.remove(goal)
                    st.success("Goal deleted")
                    st.rerun()
    
    def _create_progress_tab(self):
        """Create progress tracking tab"""
        st.subheader("📊 Progress Tracking")
        
        # Daily goals tracking
        st.subheader("📅 Daily Goals")
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Common daily goals
        daily_goals = [
            {"name": "Take Medications", "type": "medication", "target": 1},
            {"name": "Check Vitals", "type": "vitals", "target": 1},
            {"name": "Exercise", "type": "exercise", "target": 30},  # minutes
            {"name": "Hydration", "type": "hydration", "target": 8},  # glasses
            {"name": "Sleep Quality", "type": "sleep", "target": 7}  # hours
        ]
        
        for goal in daily_goals:
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"**{goal['name']}**")
            
            with col2:
                current_value = st.number_input(
                    f"Today's {goal['name']}", 
                    min_value=0, 
                    max_value=goal['target'] * 2,
                    value=self.progress_data['daily_goals'].get(f"{today}_{goal['type']}", 0),
                    key=f"daily_{goal['type']}"
                )
                self.progress_data['daily_goals'][f"{today}_{goal['type']}"] = current_value
            
            with col3:
                if current_value >= goal['target']:
                    st.success("✅ Complete!")
                else:
                    remaining = goal['target'] - current_value
                    st.info(f"Need {remaining} more")
        
        # Weekly summary
        st.subheader("📈 Weekly Summary")
        
        if st.button("📊 Generate Weekly Report"):
            self._generate_weekly_summary()
    
    def _generate_weekly_summary(self):
        """Generate weekly progress summary"""
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        
        weekly_data = []
        for i in range(7):
            date = week_start + timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            
            day_goals = {}
            for goal_type in ['medication', 'vitals', 'exercise', 'hydration', 'sleep']:
                day_goals[goal_type] = self.progress_data['daily_goals'].get(f"{date_str}_{goal_type}", 0)
            
            weekly_data.append({
                'date': date_str,
                'goals_completed': sum(1 for v in day_goals.values() if v > 0),
                'total_goals': len(day_goals)
            })
        
        # Create weekly chart
        df = pd.DataFrame(weekly_data)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['goals_completed'],
            mode='lines+markers',
            name='Goals Completed',
            line=dict(color='#28a745', width=3)
        ))
        
        fig.update_layout(
            title="Weekly Goals Completion",
            xaxis_title="Date",
            yaxis_title="Goals Completed",
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Weekly statistics
        avg_completion = df['goals_completed'].mean()
        total_completion = df['goals_completed'].sum()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Average Daily Completion", f"{avg_completion:.1f} goals")
        with col2:
            st.metric("Total Goals This Week", f"{total_completion}")
    
    def _create_achievements_tab(self):
        """Create achievements tab"""
        st.subheader(" Achievements")
        
        # Achievement categories
        achievement_categories = {
            "Consistency": [
                {"name": "First Week", "description": "Complete daily goals for 7 days", "icon": "🥇"},
                {"name": "Month Master", "description": "Complete daily goals for 30 days", "icon": ""},
                {"name": "Streak Master", "description": "Maintain a 10-day streak", "icon": "🔥"}
            ],
            "Health Goals": [
                {"name": "Goal Crusher", "description": "Complete your first health goal", "icon": "🎯"},
                {"name": "Multi-Goal Master", "description": "Complete 5 health goals", "icon": "⭐"},
                {"name": "Perfect Week", "description": "Complete all daily goals for a week", "icon": "💯"}
            ],
            "Vital Monitoring": [
                {"name": "Data Collector", "description": "Record vitals for 7 consecutive days", "icon": "📊"},
                {"name": "Health Tracker", "description": "Record vitals for 30 days", "icon": "📈"},
                {"name": "Vital Master", "description": "Maintain normal vitals for 2 weeks", "icon": "💚"}
            ]
        }
        
        # Display achievements by category
        for category, achievements in achievement_categories.items():
            st.subheader(f" {category}")
            
            for achievement in achievements:
                # Check if achievement is unlocked
                is_unlocked = any(a['name'] == achievement['name'] for a in self.achievements)
                
                if is_unlocked:
                    st.success(f"{achievement['icon']} **{achievement['name']}** - {achievement['description']}")
                else:
                    st.info(f"🔒 **{achievement['name']}** - {achievement['description']}")
        
        # Show earned achievements
        if self.achievements:
            st.subheader("🎉 Your Achievements")
            
            for achievement in self.achievements:
                earned_date = achievement.get('earned_date', 'Unknown')
                st.success(f" **{achievement['name']}** - Earned on {earned_date}")
    
    def _create_analytics_tab(self):
        """Create analytics tab"""
        st.subheader("📈 Goals Analytics")
        
        if not self.goals:
            st.info("No goals data available for analytics")
            return
        
        # Goals completion rate
        completed_goals = len([g for g in self.goals if g['status'] == 'completed'])
        total_goals = len(self.goals)
        completion_rate = (completed_goals / total_goals) * 100 if total_goals > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Goals Completion Rate", f"{completion_rate:.1f}%")
        
        with col2:
            avg_progress = sum(g['progress'] for g in self.goals if g['status'] == 'active') / len([g for g in self.goals if g['status'] == 'active']) if any(g['status'] == 'active' for g in self.goals) else 0
            st.metric("Average Progress", f"{avg_progress:.1f}%")
        
        with col3:
            high_priority_goals = len([g for g in self.goals if g['priority'] == 'High'])
            st.metric("High Priority Goals", high_priority_goals)
        
        # Goals by type
        st.subheader("📊 Goals by Type")
        
        goal_types = {}
        for goal in self.goals:
            goal_type = goal['type']
            if goal_type not in goal_types:
                goal_types[goal_type] = {'total': 0, 'completed': 0}
            goal_types[goal_type]['total'] += 1
            if goal['status'] == 'completed':
                goal_types[goal_type]['completed'] += 1
        
        if goal_types:
            type_data = []
            for goal_type, data in goal_types.items():
                completion_rate = (data['completed'] / data['total']) * 100 if data['total'] > 0 else 0
                type_data.append({
                    'Type': goal_type,
                    'Total': data['total'],
                    'Completed': data['completed'],
                    'Completion Rate': completion_rate
                })
            
            df = pd.DataFrame(type_data)
            st.dataframe(df, use_container_width=True)
    
    def _calculate_current_streak(self):
        """Calculate current daily goals streak"""
        today = datetime.now()
        streak = 0
        
        for i in range(30):  # Check last 30 days
            check_date = today - timedelta(days=i)
            date_str = check_date.strftime('%Y-%m-%d')
            
            # Check if all daily goals were completed
            daily_completions = 0
            for goal_type in ['medication', 'vitals', 'exercise', 'hydration', 'sleep']:
                if self.progress_data['daily_goals'].get(f"{date_str}_{goal_type}", 0) > 0:
                    daily_completions += 1
            
            if daily_completions >= 3:  # At least 3 goals completed
                streak += 1
            else:
                break
        
        return streak
    
    def _award_achievement(self, achievement_type, goal=None):
        """Award achievement to user"""
        achievement_map = {
            "goal_completed": {
                "name": "Goal Crusher",
                "description": "Completed your first health goal",
                "icon": ""
            },
            "streak_7": {
                "name": "First Week",
                "description": "Complete daily goals for 7 days",
                "icon": ""
            },
            "streak_30": {
                "name": "Month Master", 
                "description": "Complete daily goals for 30 days",
                "icon": ""
            }
        }
        
        if achievement_type in achievement_map:
            achievement = achievement_map[achievement_type].copy()
            achievement['earned_date'] = datetime.now().strftime('%Y-%m-%d')
            
            # Check if already earned
            if not any(a['name'] == achievement['name'] for a in self.achievements):
                self.achievements.append(achievement)
                st.balloons()  # Celebration animation
                st.success(f" Achievement Unlocked: {achievement['name']}!")
    
    def update_goal_progress(self, vitals):
        """Update goal progress based on current vitals"""
        for goal in self.goals:
            if goal['status'] != 'active':
                continue
            
            # Update progress based on goal type
            if goal['type'] == 'Heart Rate Target':
                current_hr = vitals.get('heart_rate', 0)
                target_hr = goal['target_value']
                
                if current_hr > 0:
                    # Calculate progress (closer to target = higher progress)
                    progress = max(0, 100 - abs(current_hr - target_hr) / target_hr * 100)
                    goal['progress'] = min(100, progress)
                    goal['current_value'] = current_hr
            
            elif goal['type'] == 'Blood Pressure Control':
                current_sys = vitals.get('blood_pressure_systolic', 0)
                target_sys = goal['target_value']
                
                if current_sys > 0:
                    # Normal BP range progress
                    if 90 <= current_sys <= 120:
                        goal['progress'] = 100
                    else:
                        progress = max(0, 100 - abs(current_sys - target_sys) / target_sys * 100)
                        goal['progress'] = min(100, progress)
                    goal['current_value'] = current_sys
            
            # Check if goal is completed
            if goal['progress'] >= 100 and goal['status'] == 'active':
                goal['status'] = 'completed'
                goal['completed_date'] = datetime.now().strftime('%Y-%m-%d')
                self._award_achievement("goal_completed", goal)
