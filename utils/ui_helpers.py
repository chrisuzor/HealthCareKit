"""
UI Helper Functions for Maxio Health System
Provides consistent styling and reusable UI components
"""

import streamlit as st
from config import UI_COLORS, VITAL_COLORS

def apply_custom_css():
    """Apply custom CSS styling to the application"""
    # Get selected theme from session state (default to Classic)
    theme = st.session_state.get('ui_theme', 'Classic')
    css_styles = _get_css_styles(theme)
    st.markdown(css_styles, unsafe_allow_html=True)

def _get_css_styles(theme='Classic'):
    """Get the CSS styles for the application based on selected theme"""
    if theme == 'Classic':
        return _get_classic_css()
    else:  # Modern theme
        return _get_modern_css()

def _get_modern_css():
    """Get modern theme CSS with clean, minimal design"""
    return f"""
    <style>
    /* Main application styles */
    .main {{
        background: #f5f7fa;
    }}
    
    .main-header {{
        background: linear-gradient(135deg, {UI_COLORS['primary']} 0%, {UI_COLORS['secondary']} 100%);
        padding: 2.5rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }}
    
    .main-header:hover {{
        box-shadow: 0 12px 48px rgba(0,0,0,0.12);
        transform: translateY(-2px);
    }}
    
    .main-header h1 {{
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
        letter-spacing: -0.5px;
    }}
    
    .main-header p {{
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.95;
    }}
    
    .sidebar-header {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.25rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }}
    
    .sidebar-header h3 {{
        margin: 0;
        font-weight: 600;
    }}
    
    .metric-card {{
        background: white;
        border: 1px solid #e8edf2;
        border-radius: 16px;
        padding: 1.75rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        transition: all 0.3s ease;
    }}
    
    .metric-card:hover {{
        box-shadow: 0 8px 24px rgba(0,0,0,0.08);
        transform: translateY(-4px);
        border-color: #d0d9e0;
    }}
    
    .vital-card {{
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 0.75rem 0;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }}
    
    .vital-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: var(--vital-color);
        transition: width 0.3s ease;
    }}
    
    .vital-card:hover {{
        box-shadow: 0 8px 32px rgba(0,0,0,0.12);
        transform: translateX(4px);
    }}
    
    .vital-card:hover::before {{
        width: 8px;
    }}
    
    .vital-card-clickable {{
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 0.75rem 0;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }}
    
    .vital-card-clickable::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: var(--vital-color);
        transition: width 0.3s ease;
    }}
    
    .vital-card-clickable:hover {{
        box-shadow: 0 8px 32px rgba(0,0,0,0.12);
        transform: translateX(4px);
    }}
    
    .vital-card-clickable:hover::before {{
        width: 8px;
    }}
    
    .vital-title {{
        font-size: 0.95rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.75rem;
    }}
    
    .vital-value {{
        font-size: 2.25rem;
        font-weight: 700;
        color: var(--vital-color);
        line-height: 1;
        margin: 0.5rem 0;
    }}
    
    .vital-unit {{
        font-size: 1rem;
        font-weight: 500;
        color: #94a3b8;
        margin-left: 0.5rem;
    }}
    
    .status-badge {{
        display: inline-block;
        padding: 0.35rem 0.9rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 0.75rem;
    }}
    
    .status-normal {{
        background: #d1fae5;
        color: #065f46;
    }}
    
    .status-warning {{
        background: #fed7aa;
        color: #92400e;
    }}
    
    .status-critical {{
        background: #fecaca;
        color: #991b1b;
    }}
    
    .interactive-button {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 10px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }}
    
    .interactive-button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }}
    
    .status-indicator {{
        border-left: 4px solid var(--status-color);
        background: var(--status-bg);
        padding: 1rem 1.25rem;
        border-radius: 8px;
        margin: 1rem 0;
        transition: all 0.2s ease;
    }}
    
    .status-indicator:hover {{
        border-left-width: 6px;
        padding-left: 1.5rem;
    }}
    
    /* Streamlit overrides */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        border-radius: 8px 8px 0 0;
        padding: 12px 24px;
        font-weight: 600;
    }}
    
    .stButton button {{
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s ease;
    }}
    
    .stButton button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }}
    </style>
    """

def _get_classic_css():
    """Get classic theme CSS - Dark theme with colored borders and pulsing dots"""
    return f"""
    <style>
    /* Classic Theme - Dark Design with Colored Borders */
    /* Use Streamlit's default dark background */
    .main {{
        background: transparent;
    }}
    
    /* Dark theme text colors */
    .stMarkdown, .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{
        color: #e2e8f0 !important;
    }}
    
    .main-header {{
        background: linear-gradient(135deg, {UI_COLORS['primary']} 0%, {UI_COLORS['secondary']} 100%);
        padding: 2.5rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
    }}
    
    .main-header h1 {{
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }}
    
    .main-header p {{
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.95;
    }}
    
    .sidebar-header {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.25rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }}
    
    .metric-card {{
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.75rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }}
    
    .vital-card {{
        background: rgba(30, 41, 59, 0.5);
        border: 2px solid var(--vital-color);
        border-radius: 16px;
        padding: 2rem 1.5rem;
        margin: 0.75rem 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        position: relative;
        backdrop-filter: blur(10px);
        text-align: center;
    }}
    
    .vital-card:hover {{
        box-shadow: 0 8px 32px rgba(0,0,0,0.5);
        transform: translateY(-8px) scale(1.02);
        border-color: var(--vital-color);
        background: rgba(30, 41, 59, 0.7);
    }}
    
    .vital-card-clickable {{
        background: rgba(30, 41, 59, 0.5);
        border: 2px solid var(--vital-color);
        border-radius: 16px;
        padding: 2rem 1.5rem;
        margin: 0.75rem 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        position: relative;
        backdrop-filter: blur(10px);
        text-align: center;
    }}
    
    .vital-card-clickable:hover {{
        box-shadow: 0 8px 32px rgba(0,0,0,0.5);
        transform: translateY(-8px) scale(1.02);
        border-color: var(--vital-color);
        background: rgba(30, 41, 59, 0.7);
    }}
    
    .vital-title {{
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--vital-color);
        text-transform: capitalize;
        letter-spacing: 0.5px;
        margin-bottom: 1rem;
        text-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }}
    
    .vital-value {{
        font-size: 2.75rem;
        font-weight: 700;
        color: var(--vital-color);
        line-height: 1;
        margin: 1rem 0;
        text-shadow: 0 2px 12px var(--vital-color-shadow);
        display: block;
    }}
    
    .vital-unit {{
        font-size: 1.1rem;
        font-weight: 500;
        color: var(--vital-color);
        opacity: 0.9;
        margin-left: 0;
    }}
    
    .status-indicator {{
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        margin-top: 1rem;
    }}
    
    .status-dot {{
        width: 12px;
        height: 12px;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 12px currentColor;
        animation: pulse 2s ease-in-out infinite;
    }}
    
    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.6; }}
    }}
    
    .status-text {{
        font-size: 0.9rem;
        font-weight: 500;
        text-transform: capitalize;
        letter-spacing: 0.5px;
    }}
    
    .status-normal {{
        color: #10b981;
    }}
    
    .status-normal .status-dot {{
        background: #10b981;
        color: #10b981;
    }}
    
    .status-warning {{
        color: #f59e0b;
    }}
    
    .status-warning .status-dot {{
        background: #f59e0b;
        color: #f59e0b;
    }}
    
    .status-critical {{
        color: #ef4444;
    }}
    
    .status-critical .status-dot {{
        background: #ef4444;
        color: #ef4444;
    }}
    
    .status-badge {{
        display: inline-block;
        padding: 0.35rem 0.9rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 0.75rem;
    }}
    
    .stButton button {{
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s ease;
    }}
    
    .stButton button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }}
    
    .stTabs [data-baseweb="tab"] {{
        border-radius: 8px 8px 0 0;
        padding: 12px 24px;
        font-weight: 600;
    }}
    </style>
    """

def create_header(title, subtitle=""):
    """Create a consistent header with gradient background"""
    # Clean title based on theme
    theme = st.session_state.get('ui_theme', 'Classic')
    if theme == 'Modern':
        clean_title = title.strip()  # Remove emojis for modern
    else:
        clean_title = title  # Keep emojis for classic
    
    header_html = f"""
    <div class="main-header">
        <h1>{clean_title}</h1>
        {f'<p>{subtitle}</p>' if subtitle else ''}
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

def create_sidebar_header(title):
    """Create a sidebar header with gradient background"""
    # Clean or keep emoji based on theme
    theme = st.session_state.get('ui_theme', 'Classic')
    if theme == 'Modern':
        clean_title = title.replace('🔧', '').replace('📊', '').replace('📈', '').strip()
    else:
        clean_title = title  # Keep emojis for classic
    
    sidebar_html = f"""
    <div class="sidebar-header">
        <h3>{clean_title}</h3>
    </div>
    """
    st.markdown(sidebar_html, unsafe_allow_html=True)

def display_vital_card(title, value, unit, color, status="normal"):
    """Display a vital sign in a styled card (theme-aware)"""
    status_display = status.title() if status else "Normal"
    theme = st.session_state.get('ui_theme', 'Classic')
    
    # Create color shadow for Classic theme glow effect
    color_shadow = color.replace('#', '').lower()
    r = int(color_shadow[0:2], 16)
    g = int(color_shadow[2:4], 16)
    b = int(color_shadow[4:6], 16)
    shadow_color = f"rgba({r}, {g}, {b}, 0.4)"
    
    if theme == 'Classic':
        # Dark theme with pulsing dot
        card_html = f"""
        <div class="vital-card" style="--vital-color: {color}; --vital-color-shadow: {shadow_color};">
            <div class="vital-title">{title}</div>
            <div class="vital-value">{value} <span class="vital-unit">{unit}</span></div>
            <div class="status-indicator status-{status}">
                <span class="status-dot"></span>
                <span class="status-text">{status_display}</span>
            </div>
        </div>
        """
    else:
        # Modern theme with badge
        card_html = f"""
        <div class="vital-card" style="--vital-color: {color};">
            <div class="vital-title">{title}</div>
            <div style="display: flex; align-items: baseline;">
                <span class="vital-value">{value}</span>
                <span class="vital-unit">{unit}</span>
            </div>
            <span class="status-badge status-{status}">{status_display}</span>
        </div>
        """
    
    st.markdown(card_html, unsafe_allow_html=True)

def display_clickable_vital_card(title, value, unit, color, status="normal", vital_key=""):
    """Display a clickable vital sign card that shows statistics within the same tile when clicked"""
    status_display = status.title() if status else "Normal"
    theme = st.session_state.get('ui_theme', 'Classic')
    
    # Create color shadow for Classic theme glow effect
    color_shadow = color.replace('#', '').lower()
    r = int(color_shadow[0:2], 16)
    g = int(color_shadow[2:4], 16)
    b = int(color_shadow[4:6], 16)
    shadow_color = f"rgba({r}, {g}, {b}, 0.4)"
    
    # Create unique key for this vital's button
    button_key = f"vital_btn_{vital_key}"
    
    # Check if stats are currently shown
    current_state = st.session_state.get(f"show_stats_{vital_key}", False)
    
    # Get statistics if available
    stats_content = ""
    if current_state and 'vital_monitor' in st.session_state:
        vital_monitor = st.session_state.vital_monitor
        if vital_key in vital_monitor.vital_data and len(vital_monitor.vital_data[vital_key]) > 0:
            data = vital_monitor.vital_data[vital_key]
            avg_value = sum(data) / len(data)
            max_value = max(data)
            min_value = min(data)
            
            # Format values
            avg_formatted = f"{avg_value:.1f}"
            max_formatted = f"{max_value:.1f}" if isinstance(max_value, float) else str(max_value)
            min_formatted = f"{min_value:.1f}" if isinstance(min_value, float) else str(min_value)
            
            # Calculate percentages for chart bars (relative to max value)
            max_val = float(max_value)
            avg_percent = (avg_value / max_val * 100) if max_val > 0 else 0
            min_percent = (float(min_value) / max_val * 100) if max_val > 0 else 0
            
            # Get health status for each value and assign colors
            avg_status, _ = vital_monitor.get_vital_status(vital_key, avg_value)
            max_status, _ = vital_monitor.get_vital_status(vital_key, max_value)
            min_status, _ = vital_monitor.get_vital_status(vital_key, min_value)
            
            # Status colors
            status_colors = {
                'normal': '#10b981',  # Green
                'warning': '#f59e0b',  # Orange
                'critical': '#ef4444'  # Red
            }
            
            avg_color = status_colors.get(avg_status, status_colors['normal'])
            max_color = status_colors.get(max_status, status_colors['normal'])
            min_color = status_colors.get(min_status, status_colors['normal'])
            
            if theme == 'Classic':
                stats_content = f'<div style="margin-top: 1.25rem; padding-top: 1.25rem; border-top: 2px solid rgba(255,255,255,0.15);"><div style="text-align: center; color: {color}; font-size: 0.9rem; font-weight: 700; margin-bottom: 1rem; text-transform: uppercase; letter-spacing: 1px;">Statistics Overview</div><div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;"><div style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 10px; border: 1px solid {avg_color}44;"><div style="color: #94a3b8; font-size: 0.75rem; margin-bottom: 0.5rem; font-weight: 600; text-transform: uppercase;">Average</div><div style="color: {avg_color}; font-size: 1.5rem; font-weight: 700; margin-bottom: 0.5rem;">{avg_formatted}</div><div style="background: rgba(255,255,255,0.1); height: 6px; border-radius: 3px; overflow: hidden;"><div style="background: {avg_color}; width: {avg_percent}%; height: 100%; border-radius: 3px; box-shadow: 0 0 10px {avg_color};"></div></div></div><div style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 10px; border: 1px solid {max_color}44;"><div style="color: #94a3b8; font-size: 0.75rem; margin-bottom: 0.5rem; font-weight: 600; text-transform: uppercase;">Maximum</div><div style="color: {max_color}; font-size: 1.5rem; font-weight: 700; margin-bottom: 0.5rem;">{max_formatted}</div><div style="background: rgba(255,255,255,0.1); height: 6px; border-radius: 3px; overflow: hidden;"><div style="background: {max_color}; width: 100%; height: 100%; border-radius: 3px; box-shadow: 0 0 10px {max_color};"></div></div></div><div style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 10px; border: 1px solid {min_color}44;"><div style="color: #94a3b8; font-size: 0.75rem; margin-bottom: 0.5rem; font-weight: 600; text-transform: uppercase;">Minimum</div><div style="color: {min_color}; font-size: 1.5rem; font-weight: 700; margin-bottom: 0.5rem;">{min_formatted}</div><div style="background: rgba(255,255,255,0.1); height: 6px; border-radius: 3px; overflow: hidden;"><div style="background: {min_color}; width: {min_percent}%; height: 100%; border-radius: 3px; box-shadow: 0 0 10px {min_color};"></div></div></div></div><div style="text-align: center; margin-top: 1rem; padding: 0.75rem; background: rgba(255,255,255,0.03); border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);"><span style="color: {color}; font-weight: 700; font-size: 1.1rem;">{len(data)}</span> <span style="color: #94a3b8; font-size: 0.85rem;">total readings analyzed</span></div></div>'
            else:
                stats_content = f'<div style="margin-top: 1.25rem; padding-top: 1.25rem; border-top: 2px solid #e2e8f0;"><div style="text-align: center; color: {color}; font-size: 0.9rem; font-weight: 700; margin-bottom: 1rem; text-transform: uppercase; letter-spacing: 1px;">Statistics Overview</div><div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;"><div style="background: #f8fafc; padding: 1rem; border-radius: 10px; border: 2px solid {avg_color}; box-shadow: 0 2px 8px {avg_color}33;"><div style="color: #64748b; font-size: 0.75rem; margin-bottom: 0.5rem; font-weight: 600; text-transform: uppercase;">Average</div><div style="color: {avg_color}; font-size: 1.5rem; font-weight: 700; margin-bottom: 0.5rem;">{avg_formatted}</div><div style="background: #e2e8f0; height: 6px; border-radius: 3px; overflow: hidden;"><div style="background: {avg_color}; width: {avg_percent}%; height: 100%; border-radius: 3px; transition: width 0.5s ease;"></div></div></div><div style="background: #f8fafc; padding: 1rem; border-radius: 10px; border: 2px solid {max_color}; box-shadow: 0 2px 8px {max_color}33;"><div style="color: #64748b; font-size: 0.75rem; margin-bottom: 0.5rem; font-weight: 600; text-transform: uppercase;">Maximum</div><div style="color: {max_color}; font-size: 1.5rem; font-weight: 700; margin-bottom: 0.5rem;">{max_formatted}</div><div style="background: #e2e8f0; height: 6px; border-radius: 3px; overflow: hidden;"><div style="background: {max_color}; width: 100%; height: 100%; border-radius: 3px; transition: width 0.5s ease;"></div></div></div><div style="background: #f8fafc; padding: 1rem; border-radius: 10px; border: 2px solid {min_color}; box-shadow: 0 2px 8px {min_color}33;"><div style="color: #64748b; font-size: 0.75rem; margin-bottom: 0.5rem; font-weight: 600; text-transform: uppercase;">Minimum</div><div style="color: {min_color}; font-size: 1.5rem; font-weight: 700; margin-bottom: 0.5rem;">{min_formatted}</div><div style="background: #e2e8f0; height: 6px; border-radius: 3px; overflow: hidden;"><div style="background: {min_color}; width: {min_percent}%; height: 100%; border-radius: 3px; transition: width 0.5s ease;"></div></div></div></div><div style="text-align: center; margin-top: 1rem; padding: 0.75rem; background: #f8fafc; border-radius: 8px; border: 1px solid #e2e8f0;"><span style="color: {color}; font-weight: 700; font-size: 1.1rem;">{len(data)}</span> <span style="color: #64748b; font-size: 0.85rem;">total readings analyzed</span></div></div>'
    
    # Build the card with or without stats
    if theme == 'Classic':
        # Dark theme with pulsing dot
        if stats_content:
            card_html = f'<div class="vital-card-clickable" style="--vital-color: {color}; --vital-color-shadow: {shadow_color};"><div class="vital-title">{title}</div><div class="vital-value">{value} <span class="vital-unit">{unit}</span></div><div class="status-indicator status-{status}"><span class="status-dot"></span><span class="status-text">{status_display}</span></div>{stats_content}</div>'
        else:
            card_html = f'<div class="vital-card-clickable" style="--vital-color: {color}; --vital-color-shadow: {shadow_color};"><div class="vital-title">{title}</div><div class="vital-value">{value} <span class="vital-unit">{unit}</span></div><div class="status-indicator status-{status}"><span class="status-dot"></span><span class="status-text">{status_display}</span></div></div>'
    else:
        # Modern theme with badge
        if stats_content:
            card_html = f'<div class="vital-card-clickable" style="--vital-color: {color};"><div class="vital-title">{title}</div><div style="display: flex; align-items: baseline;"><span class="vital-value">{value}</span><span class="vital-unit">{unit}</span></div><span class="status-badge status-{status}">{status_display}</span>{stats_content}</div>'
        else:
            card_html = f'<div class="vital-card-clickable" style="--vital-color: {color};"><div class="vital-title">{title}</div><div style="display: flex; align-items: baseline;"><span class="vital-value">{value}</span><span class="vital-unit">{unit}</span></div><span class="status-badge status-{status}">{status_display}</span></div>'
    
    # Simply render the card HTML
    st.markdown(card_html, unsafe_allow_html=True)
    
    # Add a styled button that matches the vital card theme
    if theme == 'Classic':
        button_style = f"""
        <style>
        div[data-testid="stButton"] button[key="{button_key}"] {{
            background: rgba(30, 41, 59, 0.6);
            border: 2px solid {color};
            color: {color};
            padding: 0.6rem 1rem;
            font-size: 0.8rem;
            font-weight: 600;
            border-radius: 10px;
            width: 100%;
            margin-top: -0.5rem;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
            backdrop-filter: blur(10px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }}
        div[data-testid="stButton"] button[key="{button_key}"]:hover {{
            background: {color};
            color: rgba(30, 41, 59, 1);
            transform: translateY(-4px);
            box-shadow: 0 8px 24px {color}88, 0 0 20px {color}66;
            border-color: {color};
        }}
        </style>
        """
    else:
        button_style = f"""
        <style>
        div[data-testid="stButton"] button[key="{button_key}"] {{
            background: white;
            border: 2px solid {color};
            color: {color};
            padding: 0.6rem 1rem;
            font-size: 0.8rem;
            font-weight: 600;
            border-radius: 10px;
            width: 100%;
            margin-top: -0.5rem;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }}
        div[data-testid="stButton"] button[key="{button_key}"]:hover {{
            background: {color};
            color: white;
            transform: translateX(4px);
            box-shadow: 0 4px 16px {color}66;
            border-color: {color};
        }}
        </style>
        """
    
    st.markdown(button_style, unsafe_allow_html=True)
    
    button_text = "Less Info" if current_state else "More Info"
    if st.button(button_text, key=button_key, help=f"Click to toggle {title} statistics"):
        st.session_state[f"show_stats_{vital_key}"] = not current_state

def display_vital_statistics(vital_key, vital_name, unit, color):
    """Display statistics (avg, max, min) for a specific vital parameter"""
    theme = st.session_state.get('ui_theme', 'Classic')
    
    # Get the vital data from the vital monitor
    vital_monitor = st.session_state.vital_monitor
    
    if vital_key not in vital_monitor.vital_data or len(vital_monitor.vital_data[vital_key]) == 0:
        st.info(f"No historical data available for {vital_name} yet.")
        return
    
    data = vital_monitor.vital_data[vital_key]
    
    # Calculate statistics
    avg_value = sum(data) / len(data)
    max_value = max(data)
    min_value = min(data)
    
    # Format values properly
    avg_formatted = f"{avg_value:.1f}"
    max_formatted = f"{max_value:.1f}" if isinstance(max_value, float) else str(max_value)
    min_formatted = f"{min_value:.1f}" if isinstance(min_value, float) else str(min_value)
    
    # Display statistics based on theme
    if theme == 'Classic':
        stats_html = f"""
        <div style="
            background: rgba(30, 41, 59, 0.6);
            border: 2px solid {color};
            border-radius: 12px;
            padding: 1.5rem;
            margin: 0.5rem 0 1rem 0;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        ">
            <div style="color: {color}; font-weight: 600; font-size: 1.1rem; margin-bottom: 1rem; text-align: center;">
                {vital_name} Statistics
            </div>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;">
                <div style="text-align: center; padding: 1rem; background: rgba(255,255,255,0.05); border-radius: 8px;">
                    <div style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 0.5rem;">AVERAGE</div>
                    <div style="color: {color}; font-size: 1.8rem; font-weight: 700;">{avg_formatted}</div>
                    <div style="color: #94a3b8; font-size: 0.75rem; margin-top: 0.25rem;">{unit}</div>
                </div>
                <div style="text-align: center; padding: 1rem; background: rgba(255,255,255,0.05); border-radius: 8px;">
                    <div style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 0.5rem;">MAXIMUM</div>
                    <div style="color: {color}; font-size: 1.8rem; font-weight: 700;">{max_formatted}</div>
                    <div style="color: #94a3b8; font-size: 0.75rem; margin-top: 0.25rem;">{unit}</div>
                </div>
                <div style="text-align: center; padding: 1rem; background: rgba(255,255,255,0.05); border-radius: 8px;">
                    <div style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 0.5rem;">MINIMUM</div>
                    <div style="color: {color}; font-size: 1.8rem; font-weight: 700;">{min_formatted}</div>
                    <div style="color: #94a3b8; font-size: 0.75rem; margin-top: 0.25rem;">{unit}</div>
                </div>
            </div>
            <div style="text-align: center; margin-top: 1rem; color: #94a3b8; font-size: 0.8rem;">
                Based on {len(data)} readings
            </div>
        </div>
        """
    else:
        # Modern theme
        stats_html = f"""
        <div style="
            background: white;
            border: 1px solid #e8edf2;
            border-radius: 16px;
            padding: 1.5rem;
            margin: 0.5rem 0 1rem 0;
            box-shadow: 0 2px 12px rgba(0,0,0,0.06);
            position: relative;
            overflow: hidden;
        ">
            <div style="
                position: absolute;
                top: 0;
                left: 0;
                width: 4px;
                height: 100%;
                background: {color};
            "></div>
            <div style="color: #64748b; font-weight: 600; font-size: 1rem; margin-bottom: 1.25rem; text-transform: uppercase; letter-spacing: 0.5px;">
                {vital_name} Statistics
            </div>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;">
                <div style="text-align: center; padding: 1.25rem; background: #f8fafc; border-radius: 12px; border: 1px solid #e2e8f0;">
                    <div style="color: #94a3b8; font-size: 0.75rem; font-weight: 600; margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 0.5px;">Average</div>
                    <div style="color: {color}; font-size: 2rem; font-weight: 700; line-height: 1;">{avg_formatted}</div>
                    <div style="color: #94a3b8; font-size: 0.8rem; margin-top: 0.5rem;">{unit}</div>
                </div>
                <div style="text-align: center; padding: 1.25rem; background: #f8fafc; border-radius: 12px; border: 1px solid #e2e8f0;">
                    <div style="color: #94a3b8; font-size: 0.75rem; font-weight: 600; margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 0.5px;">Maximum</div>
                    <div style="color: {color}; font-size: 2rem; font-weight: 700; line-height: 1;">{max_formatted}</div>
                    <div style="color: #94a3b8; font-size: 0.8rem; margin-top: 0.5rem;">{unit}</div>
                </div>
                <div style="text-align: center; padding: 1.25rem; background: #f8fafc; border-radius: 12px; border: 1px solid #e2e8f0;">
                    <div style="color: #94a3b8; font-size: 0.75rem; font-weight: 600; margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 0.5px;">Minimum</div>
                    <div style="color: {color}; font-size: 2rem; font-weight: 700; line-height: 1;">{min_formatted}</div>
                    <div style="color: #94a3b8; font-size: 0.8rem; margin-top: 0.5rem;">{unit}</div>
                </div>
            </div>
            <div style="text-align: center; margin-top: 1.25rem; color: #94a3b8; font-size: 0.85rem;">
                📊 Based on {len(data)} readings
            </div>
        </div>
        """
    
    st.markdown(stats_html, unsafe_allow_html=True)

def get_status_color_scheme(status):
    """Get color scheme for status (for programmatic use)"""
    schemes = {
        "normal": {"bg": "#d1fae5", "text": "#065f46", "border": "#10b981"},
        "warning": {"bg": "#fed7aa", "text": "#92400e", "border": "#f59e0b"},
        "critical": {"bg": "#fecaca", "text": "#991b1b", "border": "#ef4444"},
        "info": {"bg": "#dbeafe", "text": "#1e40af", "border": "#3b82f6"}
    }
    return schemes.get(status, schemes["info"])

def create_status_indicator(status, text):
    """Create a status indicator with appropriate color (theme-aware)"""
    theme = st.session_state.get('ui_theme', 'Classic')
    
    # Remove emoji from text
    clean_text = text.replace('🧪', '').replace('📡', '').replace('🟢', '').replace('🔴', '').strip()
    
    if theme == 'Classic':
        # Dark theme colors
        color_map = {
            "info": {"bg": "rgba(59, 130, 246, 0.15)", "text": "#60a5fa", "border": "#3b82f6"},
            "success": {"bg": "rgba(16, 185, 129, 0.15)", "text": "#34d399", "border": "#10b981"},
            "warning": {"bg": "rgba(245, 158, 11, 0.15)", "text": "#fbbf24", "border": "#f59e0b"},
            "critical": {"bg": "rgba(239, 68, 68, 0.15)", "text": "#f87171", "border": "#ef4444"}
        }
        scheme = color_map.get(status, color_map["info"])
        
        indicator_html = f"""
        <div class="status-indicator-box" style="
            background: {scheme['bg']};
            border: 1px solid {scheme['border']};
            border-radius: 8px;
            padding: 0.75rem 1rem;
            margin: 0.5rem 0;
        ">
            <span style="color: {scheme['text']}; font-weight: 500;">{clean_text}</span>
        </div>
        """
    else:
        # Light theme (Modern)
        scheme = get_status_color_scheme(status)
        indicator_html = f"""
        <div class="status-indicator" style="
            --status-color: {scheme['border']};
            --status-bg: {scheme['bg']};
        ">
            <strong style="color: {scheme['text']};">{clean_text}</strong>
        </div>
        """
    
    st.markdown(indicator_html, unsafe_allow_html=True)

def _get_status_color(status):
    """Get the color for a given status"""
    status_colors = {
        "success": UI_COLORS['success'],
        "warning": UI_COLORS['warning'],
        "error": UI_COLORS['danger'],
        "info": UI_COLORS['info']
    }
    return status_colors.get(status, UI_COLORS['info'])

def create_info_box(title, content):
    """Create an information box with consistent styling"""
    info_html = f"""
    <div class="metric-card">
        <h4>{title}</h4>
        <p>{content}</p>
    </div>
    """
    st.markdown(info_html, unsafe_allow_html=True)

def create_disclaimer():
    """Create the standard health disclaimer"""
    st.markdown("---")
    disclaimer_html = """
    <div style="background: #f8f9fa; padding: 1rem; border-radius: 10px; text-align: center;">
        <strong>Disclaimer:</strong> This system is for informational purposes only and should not replace professional medical advice. 
        Always consult with qualified healthcare providers for proper diagnosis and treatment.
    </div>
    """
    st.markdown(disclaimer_html, unsafe_allow_html=True) 