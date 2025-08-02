import os
import streamlit as st
from openai import OpenAI
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import base64
from PIL import Image
import io
import tempfile

# Configure Streamlit page with modern theme
st.set_page_config(
    page_title="Omega - Your AI Data Analyst",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Add emergency sidebar restore button and enhanced sidebar controls
st.markdown("""
<style>
    /* Emergency restore button - always visible */
    .emergency-restore-btn {
        position: fixed !important;
        top: 20px !important;
        left: 20px !important;
        z-index: 999999 !important;
        background: linear-gradient(135deg, #ef4444, #dc2626) !important;
        color: white !important;
        border: none !important;
        border-radius: 50px !important;
        padding: 12px 20px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        cursor: pointer !important;
        box-shadow: 0 4px 16px rgba(239, 68, 68, 0.3) !important;
        transition: all 0.3s ease !important;
        font-family: 'Inter', sans-serif !important;
        display: none !important;
    }
    
    .emergency-restore-btn:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4) !important;
        background: linear-gradient(135deg, #dc2626, #b91c1c) !important;
    }
    
    .emergency-restore-btn.show {
        display: block !important;
        animation: pulse 2s infinite !important;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 4px 16px rgba(239, 68, 68, 0.3); }
        50% { box-shadow: 0 4px 20px rgba(239, 68, 68, 0.5); }
        100% { box-shadow: 0 4px 16px rgba(239, 68, 68, 0.3); }
    }
    
    /* Enhanced expand button when sidebar is collapsed */
    [data-testid="collapsedControl"] {
        background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
        color: white !important;
        border: none !important;
        border-radius: 0 12px 12px 0 !important;
        padding: 12px 8px !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3) !important;
        transition: all 0.3s ease !important;
        font-size: 16px !important;
    }
    
    [data-testid="collapsedControl"]:hover {
        background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
        transform: translateX(4px) !important;
        box-shadow: 0 6px 16px rgba(59, 130, 246, 0.4) !important;
    }
    
    /* Sidebar visibility controls */
    .sidebar-controls {
        position: fixed !important;
        top: 80px !important;
        left: 20px !important;
        z-index: 999998 !important;
        display: flex !important;
        flex-direction: column !important;
        gap: 8px !important;
    }
    
    .sidebar-control-btn {
        background: linear-gradient(135deg, #10b981, #059669) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 8px 12px !important;
        font-size: 12px !important;
        font-weight: 500 !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 8px rgba(16, 185, 129, 0.2) !important;
    }
    
    .sidebar-control-btn:hover {
        background: linear-gradient(135deg, #059669, #047857) !important;
        transform: translateY(-1px) !important;
    }
</style>

<script>
// Enhanced sidebar management system
(function() {
    let sidebarCheckInterval;
    let emergencyButton;
    
    function createEmergencyButton() {
        if (emergencyButton) return;
        
        emergencyButton = document.createElement('button');
        emergencyButton.className = 'emergency-restore-btn';
        emergencyButton.innerHTML = '📤 Show Upload Panel';
        emergencyButton.onclick = function() {
            restoreSidebar();
            hideEmergencyButton();
        };
        document.body.appendChild(emergencyButton);
    }
    
    function showEmergencyButton() {
        if (emergencyButton) {
            emergencyButton.classList.add('show');
        }
    }
    
    function hideEmergencyButton() {
        if (emergencyButton) {
            emergencyButton.classList.remove('show');
        }
    }
    
    function createSidebarControls() {
        const controlsDiv = document.createElement('div');
        controlsDiv.className = 'sidebar-controls';
        controlsDiv.innerHTML = `
            <button class="sidebar-control-btn" onclick="restoreSidebar()">📤 Restore</button>
            <button class="sidebar-control-btn" onclick="toggleSidebar()">↔️ Toggle</button>
        `;
        document.body.appendChild(controlsDiv);
    }
    
    function restoreSidebar() {
        const sidebar = document.querySelector('[data-testid="stSidebar"]');
        const collapsedControl = document.querySelector('[data-testid="collapsedControl"]');
        
        if (sidebar) {
            sidebar.style.transform = 'translateX(0px)';
            sidebar.style.visibility = 'visible';
            sidebar.style.display = 'block';
            sidebar.style.minWidth = '244px';
            sidebar.style.maxWidth = '550px';
        }
        
        if (collapsedControl) {
            collapsedControl.click();
        }
        
        // Force Streamlit to recognize sidebar state change
        setTimeout(() => {
            const event = new CustomEvent('streamlit:sidebarStateChange', { 
                detail: { expanded: true } 
            });
            window.dispatchEvent(event);
        }, 100);
    }
    
    function toggleSidebar() {
        const sidebar = document.querySelector('[data-testid="stSidebar"]');
        const collapsedControl = document.querySelector('[data-testid="collapsedControl"]');
        
        if (sidebar) {
            const isHidden = sidebar.style.transform === 'translateX(-100%)' || 
                           sidebar.style.display === 'none' ||
                           !sidebar.offsetParent;
            
            if (isHidden) {
                restoreSidebar();
            } else {
                // Collapse sidebar
                const collapseBtn = sidebar.querySelector('[data-testid="baseButton-header"]');
                if (collapseBtn) {
                    collapseBtn.click();
                }
            }
        }
    }
    
    function checkSidebarVisibility() {
        const sidebar = document.querySelector('[data-testid="stSidebar"]');
        const isHidden = !sidebar || 
                        sidebar.style.transform === 'translateX(-100%)' || 
                        sidebar.style.display === 'none' ||
                        !sidebar.offsetParent ||
                        sidebar.offsetWidth < 50;
        
        if (isHidden) {
            showEmergencyButton();
        } else {
            hideEmergencyButton();
        }
    }
    
    // Make functions globally available
    window.restoreSidebar = restoreSidebar;
    window.toggleSidebar = toggleSidebar;
    
    // Initialize
    function init() {
        createEmergencyButton();
        createSidebarControls();
        
        // Start monitoring sidebar visibility
        sidebarCheckInterval = setInterval(checkSidebarVisibility, 500);
        
        // Initial check
        setTimeout(checkSidebarVisibility, 1000);
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    // Also initialize when Streamlit loads
    setTimeout(init, 2000);
})();
</script>
""", unsafe_allow_html=True)

# Modern styling to match the landing page design
st.markdown("""
<style>
    /* Import modern fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800;900&display=swap');
    
    /* Force light theme */
    .stApp {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
    }
    
    /* Override all backgrounds to white */
    .main .block-container {
        background-color: #ffffff !important;
        padding-top: 1rem !important;
        max-width: 1200px !important;
    }
    
    /* Sidebar styling - Enhanced with better controls */
    .css-1d391kg, .css-1lcbmhc, .css-17lntkn, section[data-testid="stSidebar"] {
        background-color: #f8fafc !important;
        border-right: 1px solid #e2e8f0 !important;
        visibility: visible !important;
        display: block !important;
        transition: all 0.3s ease !important;
    }
    
    /* Allow resizable sidebar */
    section[data-testid="stSidebar"] > div {
        min-width: 244px !important;
        max-width: 550px !important;
        resize: horizontal !important;
        overflow: auto !important;
    }
    
    /* Enhanced collapse button styling */
    section[data-testid="stSidebar"] [data-testid="baseButton-header"] {
        background: linear-gradient(135deg, #64748b, #475569) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 8px 12px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 8px rgba(100, 116, 139, 0.2) !important;
    }
    
    section[data-testid="stSidebar"] [data-testid="baseButton-header"]:hover {
        background: linear-gradient(135deg, #475569, #334155) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(100, 116, 139, 0.3) !important;
    }
    
    /* Sidebar content styling */
    .css-1lcbmhc .css-1v0mbdj {
        display: block !important;
        visibility: visible !important;
        padding: 1rem !important;
    }
    
    /* Add restore hint when sidebar might be hidden */
    .sidebar-hint {
        position: fixed !important;
        bottom: 20px !important;
        left: 20px !important;
        background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
        color: white !important;
        padding: 8px 16px !important;
        border-radius: 20px !important;
        font-size: 12px !important;
        font-weight: 500 !important;
        z-index: 999997 !important;
        opacity: 0 !important;
        transform: translateY(20px) !important;
        transition: all 0.3s ease !important;
        pointer-events: none !important;
    }
    
    .sidebar-hint.show {
        opacity: 1 !important;
        transform: translateY(0) !important;
    }
    
    /* Base typography */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
        background-color: #ffffff !important;
        color: #1a1a1a !important;
    }
    
    /* Landing page hero section */
    .hero-section {
        background: #ffffff !important;
        padding: 4rem 2rem !important;
        text-align: center !important;
        color: #1a1a1a !important;
        margin-bottom: 3rem !important;
    }
    
    .hero-icon {
        font-size: 4rem !important;
        margin-bottom: 2rem !important;
        color: #374151 !important;
    }
    
    .hero-title {
        font-size: 3.5rem !important;
        font-weight: 700 !important;
        margin-bottom: 1rem !important;
        font-family: 'Inter', sans-serif !important;
        color: #111827 !important;
        line-height: 1.1 !important;
    }
    
    .hero-subtitle {
        font-size: 1.25rem !important;
        font-weight: 400 !important;
        color: #6b7280 !important;
        margin-bottom: 3rem !important;
        max-width: 600px !important;
        margin-left: auto !important;
        margin-right: auto !important;
        line-height: 1.6 !important;
    }
    
    .cta-button {
        background: #1f2937 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.875rem 2rem !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 1rem !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
        text-decoration: none !important;
        display: inline-flex !important;
        align-items: center !important;
        gap: 0.5rem !important;
    }
    
    .cta-button:hover {
        background: #111827 !important;
        transform: translateY(-1px) !important;
    }
    
    /* Features grid */
    .features-grid {
        display: flex !important;
        flex-wrap: wrap !important;
        gap: 2rem !important;
        margin: 3rem 0 !important;
        justify-content: center !important;
    }
    
    .feature-card {
        background: #ffffff !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 12px !important;
        padding: 2rem !important;
        text-align: center !important;
        flex: 1 !important;
        min-width: 250px !important;
        max-width: 300px !important;
        transition: all 0.2s ease !important;
    }
    
    .feature-card:hover {
        border-color: #d1d5db !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05) !important;
    }
    
    .feature-icon {
        width: 48px !important;
        height: 48px !important;
        margin: 0 auto 1.5rem auto !important;
        background: #f3f4f6 !important;
        border-radius: 8px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 1.5rem !important;
    }
    
    .feature-icon.upload { color: #3b82f6 !important; }
    .feature-icon.chat { color: #10b981 !important; }
    .feature-icon.chart { color: #8b5cf6 !important; }
    .feature-icon.ai { color: #f59e0b !important; }
    
    .feature-title {
        font-size: 1.125rem !important;
        font-weight: 600 !important;
        color: #111827 !important;
        margin-bottom: 0.75rem !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .feature-description {
        font-size: 0.875rem !important;
        color: #6b7280 !important;
        line-height: 1.5 !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Why choose section */
    .why-choose-section {
        background: #f9fafb !important;
        padding: 4rem 2rem !important;
        border-radius: 16px !important;
        margin: 4rem 0 !important;
        text-align: center !important;
    }
    
    .why-choose-title {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #111827 !important;
        margin-bottom: 1rem !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .why-choose-subtitle {
        font-size: 1rem !important;
        color: #6b7280 !important;
        margin-bottom: 3rem !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .stats-grid {
        display: flex !important;
        justify-content: center !important;
        gap: 6rem !important;
        flex-wrap: wrap !important;
    }
    
    .stat-item {
        text-align: center !important;
    }
    
    .stat-value {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        color: #111827 !important;
        display: block !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .stat-label {
        font-size: 0.875rem !important;
        color: #6b7280 !important;
        font-weight: 500 !important;
        margin-top: 0.5rem !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .stat-description {
        font-size: 0.75rem !important;
        color: #9ca3af !important;
        margin-top: 0.25rem !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Chat interface styling */
    .chat-container {
        background-color: #ffffff !important;
        border-radius: 16px !important;
        padding: 2rem !important;
        margin-bottom: 1rem !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05) !important;
    }
    
    .user-message {
        background: linear-gradient(135deg, #1a1a1a, #000000) !important;
        color: white !important;
        padding: 1.2rem 1.8rem !important;
        border-radius: 20px 20px 4px 20px !important;
        margin: 1rem 0 !important;
        margin-left: 20% !important;
        font-weight: 500 !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%) !important;
        color: #1e293b !important;
        padding: 1.2rem 1.8rem !important;
        border-radius: 20px 20px 20px 4px !important;
        margin: 1rem 0 !important;
        margin-right: 20% !important;
        border-left: 4px solid #000000 !important;
        font-weight: 400 !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08) !important;
        border: 1px solid #e2e8f0 !important;
    }
    
    .error-message {
        background: linear-gradient(135deg, #fef2f2 0%, #ffffff 100%) !important;
        color: #dc2626 !important;
        padding: 1.2rem 1.8rem !important;
        border-radius: 16px !important;
        margin: 1rem 0 !important;
        border-left: 4px solid #ef4444 !important;
        font-weight: 500 !important;
        box-shadow: 0 4px 16px rgba(239, 68, 68, 0.1) !important;
    }
    
    /* Streaming insights styling */
    .streaming-insights {
        background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%) !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 16px !important;
        padding: 1.5rem !important;
        margin: 1rem 0 !important;
        border-left: 4px solid #3b82f6 !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05) !important;
    }
    
    /* Input styling */
    .stTextInput > div > div > input, .stChatInput > div > div > input {
        background-color: #ffffff !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 16px !important;
        color: #1a1a1a !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 1rem !important;
        padding: 1rem 1.5rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus, .stChatInput > div > div > input:focus {
        border-color: #1a1a1a !important;
        box-shadow: 0 0 0 4px rgba(26, 26, 26, 0.1) !important;
        outline: none !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #1a1a1a 0%, #000000 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 16px !important;
        padding: 1rem 2.5rem !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.25) !important;
    }
    
    /* Metrics cards */
    .metric-card {
        background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%) !important;
        padding: 2rem !important;
        border-radius: 16px !important;
        border: 1px solid #e2e8f0 !important;
        text-align: center !important;
        color: #1e293b !important;
        font-family: 'Inter', sans-serif !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05) !important;
        transition: all 0.3s ease !important;
    }
    
    .metric-card:hover {
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1) !important;
        transform: translateY(-4px) !important;
    }
    
    .metric-card h4 {
        color: #64748b !important;
        font-size: 0.875rem !important;
        font-weight: 600 !important;
        margin-bottom: 0.75rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
    }
    
    .metric-card h2 {
        color: #1a1a1a !important;
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        margin: 0 !important;
        font-family: 'Poppins', sans-serif !important;
    }
    
    /* File uploader */
    .uploadedFile {
        background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%) !important;
        border: 2px dashed #94a3b8 !important;
        border-radius: 16px !important;
        padding: 3rem !important;
        text-align: center !important;
        color: #475569 !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.3s ease !important;
    }
    
    .uploadedFile:hover {
        border-color: #1a1a1a !important;
        background: linear-gradient(135deg, #f1f5f9 0%, #ffffff 100%) !important;
    }
    
    /* Override Streamlit's default text colors */
    .stMarkdown, .stMarkdown p, .stText, div[data-testid="stMarkdownContainer"] p {
        color: #1e293b !important;
        font-family: 'Inter', sans-serif !important;
        line-height: 1.7 !important;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #1a1a1a !important;
        font-family: 'Poppins', sans-serif !important;
        font-weight: 700 !important;
    }
    
    /* Success and info messages */
    .stSuccess {
        background-color: #f0fdf4 !important;
        border: 1px solid #22c55e !important;
        color: #15803d !important;
        border-radius: 12px !important;
    }
    
    .stInfo {
        background-color: #f0f9ff !important;
        border: 1px solid #3b82f6 !important;
        color: #1d4ed8 !important;
        border-radius: 12px !important;
    }
    
    .stError {
        background-color: #fef2f2 !important;
        border: 1px solid #ef4444 !important;
        color: #dc2626 !important;
        border-radius: 12px !important;
    }
    
    /* Loading spinner */
    .loading-container {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        padding: 2rem !important;
    }
    
    .spinner {
        border: 4px solid #f3f4f6 !important;
        border-top: 4px solid #1a1a1a !important;
        border-radius: 50% !important;
        width: 40px !important;
        height: 40px !important;
        animation: spin 1s linear infinite !important;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Chat input area */
    .stChatInput {
        background-color: #ffffff !important;
        border-top: 1px solid #e2e8f0 !important;
        padding: 1rem 0 !important;
    }
    
    /* Column styling */
    .stColumn {
        background-color: #ffffff !important;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Responsive design */
    @media (max-width: 768px) {
        .features-grid {
            flex-direction: column !important;
            align-items: center !important;
        }
        
        .feature-card {
            max-width: 100% !important;
        }
        
        .stats-grid {
            gap: 3rem !important;
            flex-direction: column !important;
        }
        
        .hero-title {
            font-size: 2.5rem !important;
        }
        
        .hero-subtitle {
            font-size: 1.125rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize OpenAI client with comprehensive diagnostics and improved timeout handling
def init_openai():
    try:
        api_key = None
        
        # Method 1: Streamlit secrets
        try:
            api_key = st.secrets.get("OPENAI_API_KEY")
        except Exception:
            pass
        
        # Method 2: Environment variable
        if not api_key:
            api_key = os.getenv("OPENAI_API_KEY")
        
        # Method 3: Direct input from user
        if not api_key:
            st.error("🔑 OpenAI API key not found!")
            st.info("Please add your OpenAI API key in one of these ways:")
            st.code("""
# Method 1: Streamlit secrets (.streamlit/secrets.toml)
OPENAI_API_KEY = "your-api-key-here"

# Method 2: Environment variable  
export OPENAI_API_KEY="your-api-key-here"
            """)
            
            # Allow user to input API key directly
            api_key = st.text_input("🔑 Enter your OpenAI API Key:", type="password", key="api_key_input")
            
            if not api_key:
                st.warning("Please enter your OpenAI API key to continue.")
                st.stop()
        
        # Validate API key format
        if not api_key.startswith('sk-'):
            st.error("❌ Invalid API key format. OpenAI keys should start with 'sk-'")
            st.stop()
        
        # Test basic connectivity first
        import requests
        try:
            # Test basic internet connectivity
            response = requests.get("https://httpbin.org/status/200", timeout=15)
        except Exception as e:
            st.error(f"❌ Internet connectivity issue: {str(e)}")
            st.info("Please check your internet connection or VPN settings")
            st.stop()
        
        # Initialize OpenAI client with improved timeout settings
        try:
            client = OpenAI(
                api_key=api_key,
                timeout=90.0,
                max_retries=2
            )
            
            test_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=1,
                temperature=0,
                timeout=30.0
            )
            
            if test_response and test_response.choices:
                return client
            else:
                raise Exception("Empty response from OpenAI API")
                
        except Exception as e:
            error_msg = str(e).lower()
            
            # Detailed error analysis
            if "timeout" in error_msg:
                st.error("❌ Request timeout occurred")
                st.info("🔧 **Possible Solutions:**")
                st.markdown("""
                1. **Check your internet speed** - Slow connections can cause timeouts
                2. **Disable VPN temporarily** - Some VPNs block or slow API requests
                3. **Try from a different network** - Corporate networks often block APIs
                4. **Check OpenAI status** - Visit https://status.openai.com/
                5. **Try again in a few minutes** - Temporary network issues
                """)
                
            elif "api key" in error_msg or "authentication" in error_msg or "401" in error_msg:
                st.error("❌ Invalid API key")
                st.info("Please verify your API key at: https://platform.openai.com/api-keys")
                
            elif "rate limit" in error_msg or "429" in error_msg:
                st.error("❌ Rate limit exceeded")
                st.info("Please wait a few minutes before trying again")
                
            elif "insufficient_quota" in error_msg or "billing" in error_msg:
                st.error("❌ Insufficient quota or billing issue")
                st.info("Check your OpenAI account billing at: https://platform.openai.com/account/billing")
                
            elif "connection" in error_msg or "network" in error_msg:
                st.error("❌ Network connection issue")
                st.info("This is likely a network/firewall issue. Try:")
                st.markdown("""
                - Different internet connection
                - Disable VPN/proxy
                - Check corporate firewall settings
                """)
                
            else:
                st.error(f"❌ Unexpected error: {str(e)}")
                st.info("Please try again or contact support if the issue persists")
            
            st.stop()
            
    except Exception as e:
        st.error(f"❌ Critical error initializing OpenAI client: {str(e)}")
        st.stop()

def query_agent(data, query, client):
    """Query Checker Agent - intelligently verifies if user request can be fulfilled with available data"""
    try:
        system_prompt = """
Role: You are an intelligent Query Checker Agent. Your job is to determine if a user's data analysis request can be fulfilled using the available dataset columns.

Instructions:
- Analyze the user's query to understand what they want to visualize or analyze
- Look at the available dataset columns and sample data
- Consider partial matches, synonyms, and related concepts
- The user might refer to columns using different names (e.g., "price" for "Price", "sales" for "Sales_Amount")
- Focus on whether the CONCEPT can be analyzed, not exact word matching
- Be PERMISSIVE - if there's any reasonable way to fulfill the request, return "yes"
- Only return "no" if the request is completely impossible with the available data

Examples:
- Query: "compare sales and profit" → If dataset has "Sales" and "Profit" columns → "yes"
- Query: "show revenue trends" → If dataset has any revenue/sales/income column → "yes"  
- Query: "analyze customer age distribution" → If dataset has age-related column → "yes"
- Query: "plot temperature vs humidity" → If dataset has no weather data → "no"

Response: Return ONLY "yes" or "no" - nothing else.
"""
        
        # Enhanced dataset info with column descriptions
        column_info = []
        for col in data.columns:
            sample_values = data[col].dropna().head(3).tolist()
            column_info.append(f"'{col}' (type: {data[col].dtype}, samples: {sample_values})")
        
        dataset_info = f"""
Dataset Columns: {list(data.columns)}
Column Details:
{chr(10).join(column_info)}

Dataset Shape: {data.shape[0]} rows, {data.shape[1]} columns
Sample Data:
{data.head(3).to_string()}
"""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Dataset Information:\n{dataset_info}\n\nUser Query: {query}\n\nCan this query be fulfilled with the available data?"}
            ],
            max_tokens=5,
            temperature=0,
            timeout=30.0
        )
        
        result = response.choices[0].message.content.strip().lower()
        
        # Debug information (remove in production)
        if result == "no":
            st.warning(f"🔍 Query validation failed for: '{query}'")
            with st.expander("Debug: Why was this rejected?"):
                st.write("Available columns:", list(data.columns))
                st.write("Query:", query)
                st.write("Validation result:", result)
        
        return result
        
    except Exception as e:
        st.error(f"Error in query validation: {str(e)}")
        # If validation fails, assume query is valid to avoid blocking legitimate requests
        return "yes"

def coder_agent(data, query, client):
    """Coder Agent - generates matplotlib visualization code with intelligent column matching"""
    try:
        system_prompt = """
Role: You are an advanced visualization agent that creates Python code using matplotlib for data visualization.

IMPORTANT INSTRUCTIONS:
1. The dataset columns are provided with their exact names - use them EXACTLY as shown
2. Be flexible with user language - they might say "sales" when column is "Sales" or "Sales_Amount"
3. Look at sample data to understand what each column contains
4. Choose appropriate visualization types based on data types and user request
5. Handle missing values gracefully
6. Create professional, well-labeled visualizations

Technical Requirements:
- Use matplotlib and pandas only
- Data is available as DataFrame named 'data'
- Start with: fig, ax = plt.subplots(figsize=(12, 8))
- End with: plt.savefig('plot.png', dpi=300, bbox_inches='tight'); plt.close()
- NO plt.show()
- Apply modern styling and good color schemes
- Include proper titles, axis labels, and legends
- Handle data type conversions if needed

Return ONLY executable Python code with no markdown formatting.
"""

        # Provide comprehensive dataset information
        column_details = []
        for col in data.columns:
            dtype = str(data[col].dtype)
            non_null = data[col].count()
            unique_vals = data[col].nunique()
            sample_vals = data[col].dropna().head(5).tolist()
            
            column_details.append(f"""
Column: '{col}'
- Type: {dtype}
- Non-null values: {non_null}/{len(data)}
- Unique values: {unique_vals}
- Sample values: {sample_vals}""")

        dataset_info = f"""
EXACT COLUMN NAMES: {list(data.columns)}
Dataset Shape: {data.shape[0]} rows × {data.shape[1]} columns

COLUMN DETAILS:
{''.join(column_details)}

SAMPLE DATA:
{data.head().to_string()}

IMPORTANT: Use the exact column names as shown above. For example:
- If user says "sales" but column is "Sales", use data['Sales']
- If user says "revenue" but column is "Total_Revenue", use data['Total_Revenue']
"""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"{dataset_info}\n\nUser Request: {query}\n\nGenerate visualization code:"}
            ],
            max_tokens=1200,
            temperature=0.2,
            timeout=45.0
        )
        
        code = response.choices[0].message.content.strip()
        
        # Clean code formatting
        if code.startswith("```python"):
            code = code[9:]
        elif code.startswith("```"):
            code = code[3:]
        if code.endswith("```"):
            code = code[:-3]
        
        return code.strip()
        
    except Exception as e:
        st.error(f"Error generating visualization code: {str(e)}")
        return None

def insights_agent_stream(image_bytes, query, client):
    """Insights Agent - generates streaming insights from visualization"""
    try:
        encoded_image = base64.b64encode(image_bytes).decode('utf-8')
        image_data_url = f"data:image/png;base64,{encoded_image}"
        
        # Create streaming completion
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text", 
                            "text": f"""Analyze this visualization created for: '{query}'. 

Provide detailed insights about patterns, trends, and key findings. Structure your response with clear headings and organized sections.

Focus on:
1. **Key Observations** - What stands out immediately?
2. **Data Patterns** - Any trends, correlations, or distributions?
3. **Business Insights** - What decisions could be made from this data?
4. **Recommendations** - What actions should be taken based on these findings?

Be specific with numbers and percentages where visible. Make your analysis actionable and insightful."""
                        },
                        {
                            "type": "image_url", 
                            "image_url": {"url": image_data_url}
                        }
                    ]
                }
            ],
            max_tokens=1500,
            temperature=0.3,
            stream=True  # Enable streaming
        )
        
        return stream
        
    except Exception as e:
        st.error(f"Error generating streaming insights: {str(e)}")
        return None

def process_query_stream(data, query, client):
    """Central controller for processing user queries with streaming insights"""
    try:
        # Step 1: Validate query
        with st.spinner("🔍 Validating your query..."):
            is_valid = query_agent(data, query, client)
        
        if is_valid == "no":
            return "❌ The attributes you're looking for are not present in the dataset. Please check the available columns and try again.", None, None
        
        # Step 2: Generate visualization
        with st.spinner("📊 Creating your visualization..."):
            code = coder_agent(data, query, client)
            
            if not code:
                return "❌ Failed to generate visualization code.", None, None
            
            # Execute code in temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                plot_path = os.path.join(temp_dir, 'plot.png')
                
                # Execute the generated code
                exec_globals = {
                    'data': data, 
                    'plt': plt, 
                    'pd': pd, 
                    'np': np,
                    'os': os
                }
                
                # Modify code to save in temp directory
                modified_code = code.replace("'plot.png'", f"'{plot_path}'")
                
                try:
                    exec(modified_code, exec_globals)
                except Exception as e:
                    return f"❌ Error executing visualization code: {str(e)}", None, None
                
                # Read the generated plot
                if os.path.exists(plot_path):
                    with open(plot_path, 'rb') as f:
                        image_bytes = f.read()
                else:
                    return "❌ Failed to generate visualization file.", None, None
        
        # Step 3: Generate streaming insights
        insights_stream = insights_agent_stream(image_bytes, query, client)
        
        return "success", image_bytes, insights_stream
        
    except Exception as e:
        return f"❌ Error processing query: {str(e)}", None, None

def display_streaming_insights(insights_stream):
    """Display insights with streaming effect"""
    if insights_stream is None:
        st.error("Failed to generate insights stream")
        return
    
    # Create a container for streaming insights
    insights_container = st.container()
    
    with insights_container:
        st.markdown("### 🧠 AI Analysis")
        
        # Create placeholder for streaming text
        text_placeholder = st.empty()
        
        # Collect streaming response
        full_response = ""
        
        try:
            for chunk in insights_stream:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    # Update the placeholder with current text
                    text_placeholder.markdown(f"""
                    <div class="streaming-insights">
                        {full_response}
                    </div>
                    """, unsafe_allow_html=True)
                    
        except Exception as e:
            st.error(f"Error during streaming: {str(e)}")
            text_placeholder.markdown(f"""
            <div class="streaming-insights">
                {full_response}
                
                <br><br><em>⚠️ Streaming interrupted, but analysis is complete above.</em>
            </div>
            """, unsafe_allow_html=True)

def show_landing_page():
    """Display the landing page that matches the design"""
    # Hero Section
    st.markdown("""
    <div class="hero-section">
        <div class="hero-icon">⚙️</div>
        <h1 class="hero-title">Omega - Your AI Data Analyst</h1>
        <p class="hero-subtitle">Turn your spreadsheets into insights through conversation. No SQL, no coding, just natural language questions about your data.</p>
        <button class="cta-button">Start Analyzing Data →</button>
    </div>
    """, unsafe_allow_html=True)
    
    # Features Grid - Using containers instead of raw HTML to prevent code display
    st.markdown('<div class="features-grid">', unsafe_allow_html=True)
    
    # Create 4 columns for features
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon upload">📤</div>
            <h3 class="feature-title">Easy Upload</h3>
            <p class="feature-description">Drag & drop CSV/Excel files. Automatic data preview and column detection with smart validation.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon chat">💬</div>
            <h3 class="feature-title">Natural Language</h3>
            <p class="feature-description">Ask questions like "show me sales trends" or "compare revenue by region" in plain English.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon chart">📊</div>
            <h3 class="feature-title">Auto Visualization</h3>
            <p class="feature-description">AI generates appropriate charts and graphs with professional styling and smart labeling.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon ai">🧠</div>
            <h3 class="feature-title">AI Insights</h3>
            <p class="feature-description">Real-time analysis with pattern identification and business recommendations.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Why Choose Section
    st.markdown("""
    <div class="why-choose-section">
        <h2 class="why-choose-title">Why Choose Omega AI?</h2>
        <p class="why-choose-subtitle">Transform anyone into a data analyst through conversation</p>
        <div class="stats-grid">
            <div class="stat-item">
                <span class="stat-value">&lt; 30s</span>
                <div class="stat-label">Time to First Insight</div>
                <div class="stat-description">From upload to visualization</div>
            </div>
            <div class="stat-item">
                <span class="stat-value">0</span>
                <div class="stat-label">Coding Required</div>
                <div class="stat-description">Pure natural language interface</div>
            </div>
            <div class="stat-item">
                <span class="stat-value">∞</span>
                <div class="stat-label">Question Types</div>
                <div class="stat-description">Ask anything about your data</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def main():
    # Initialize OpenAI client
    client = init_openai()
    
    # Sidebar for file upload and dataset info
    with st.sidebar:
        st.markdown("### Upload Your Dataset")
        uploaded_file = st.file_uploader(
            "Choose a CSV or Excel file",
            type=['csv', 'xlsx', 'xls'],
            help="Upload your dataset to start analyzing"
        )
        
        if uploaded_file:
            try:
                # Load data
                if uploaded_file.name.endswith('.csv'):
                    data = pd.read_csv(uploaded_file)
                else:
                    data = pd.read_excel(uploaded_file)
                
                st.success(f"✅ Dataset loaded successfully!")
                
                # Dataset overview
                st.markdown("### Dataset Overview")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>Rows</h4>
                        <h2>{data.shape[0]:,}</h2>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>Columns</h4>
                        <h2>{data.shape[1]}</h2>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Column information
                st.markdown("### Available Columns")
                for col in data.columns:
                    st.markdown(f"• **{col}** ({data[col].dtype})")
                
                # Sample data
                with st.expander("👀 Preview Data"):
                    st.dataframe(data.head(), use_container_width=True)
                
            except Exception as e:
                st.error(f"❌ Error loading dataset: {str(e)}")
                data = None
        else:
            data = None
            st.info("👆 Please upload a dataset to get started")
    
    # Main content area
    if data is not None:
        # Show Omega header when data is loaded
        st.markdown("""
        <div class="hero-section" style="padding: 2rem; margin-bottom: 1rem;">
            <div class="hero-icon" style="font-size: 2.5rem; margin-bottom: 1rem;">⚙️</div>
            <h1 class="hero-title" style="font-size: 2.5rem; margin-bottom: 0.5rem;">Omega</h1>
            <p class="hero-subtitle" style="font-size: 1rem; margin-bottom: 0;">Multi-Agentic System for Intelligent Data Analysis</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        st.markdown("### 💬 Chat with Your Data")
        
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {
                    "role": "assistant", 
                    "content": "Hello! I'm Omega, your AI data analyst. I can help you visualize and analyze your data with streaming insights. What would you like to explore?",
                    "type": "text"
                }
            ]
        
        # Display chat history
        for i, message in enumerate(st.session_state.messages):
            if message["role"] == "user":
                st.markdown(f"""
                <div class="user-message">
                    <strong>You:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                if message["type"] == "text":
                    st.markdown(f"""
                    <div class="assistant-message">
                        <strong>Omega:</strong> {message["content"]}
                    </div>
                    """, unsafe_allow_html=True)
                elif message["type"] == "visualization":
                    st.markdown(f"""
                    <div class="assistant-message">
                        <strong>Omega:</strong> Here's your visualization with streaming analysis:
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Display visualization
                    st.image(message["image"], caption="Generated Visualization", use_column_width=True)
                    
                    # Display stored insights (for chat history)
                    if "insights" in message:
                        st.markdown(f"""
                        <div class="streaming-insights">
                            <h3>🧠 AI Analysis</h3>
                            {message["insights"]}
                        </div>
                        """, unsafe_allow_html=True)
                        
                elif message["type"] == "error":
                    st.markdown(f"""
                    <div class="error-message">
                        <strong>Omega:</strong> {message["content"]}
                    </div>
                    """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Chat input
        user_query = st.chat_input("Ask me anything about your data...")
        
        if user_query:
            # Add user message
            st.session_state.messages.append({
                "role": "user", 
                "content": user_query,
                "type": "text"
            })
            
            # Rerun to show user message immediately
            st.rerun()
            
        # Process query if there's a new user message
        if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
            last_user_message = st.session_state.messages[-1]["content"]
            
            # Process query with streaming
            result, image_bytes, insights_stream = process_query_stream(data, last_user_message, client)
            
            if result == "success" and image_bytes and insights_stream:
                # Display the assistant's response header
                st.markdown(f"""
                <div class="assistant-message">
                    <strong>Omega:</strong> Here's your visualization with streaming analysis:
                </div>
                """, unsafe_allow_html=True)
                
                # Display visualization
                st.image(image_bytes, caption="Generated Visualization", use_column_width=True)
                
                # Stream insights in real-time
                insights_container = st.container()
                with insights_container:
                    st.markdown("### 🧠 AI Analysis")
                    
                    # Create placeholder for streaming text
                    text_placeholder = st.empty()
                    
                    # Collect streaming response
                    full_response = ""
                    
                    try:
                        for chunk in insights_stream:
                            if chunk.choices[0].delta.content is not None:
                                full_response += chunk.choices[0].delta.content
                                # Update the placeholder with current text
                                text_placeholder.markdown(f"""
                                <div class="streaming-insights">
                                    {full_response}
                                </div>
                                """, unsafe_allow_html=True)
                                
                    except Exception as e:
                        st.error(f"Error during streaming: {str(e)}")
                        text_placeholder.markdown(f"""
                        <div class="streaming-insights">
                            {full_response}
                            
                            <br><br><em>⚠️ Streaming interrupted, but analysis is complete above.</em>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Add to chat history (with final insights for persistence)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "Here's your visualization with streaming analysis:",
                    "type": "visualization",
                    "image": image_bytes,
                    "insights": full_response
                })
                
            else:
                # Add error message
                st.markdown(f"""
                <div class="error-message">
                    <strong>Omega:</strong> {result}
                </div>
                """, unsafe_allow_html=True)
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result,
                    "type": "error"
                })
    
    else:
        # Show landing page when no data is uploaded
        show_landing_page()

if __name__ == "__main__":
    main()
