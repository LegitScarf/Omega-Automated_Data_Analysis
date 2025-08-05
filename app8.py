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
    
    /* Chat type indicators */
    .chat-mode-indicator {
        background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
        color: white !important;
        padding: 4px 12px !important;
        border-radius: 20px !important;
        font-size: 0.75rem !important;
        font-weight: 500 !important;
        display: inline-block !important;
        margin-bottom: 0.5rem !important;
    }
    
    .chat-mode-indicator.analyze {
        background: linear-gradient(135deg, #10b981, #059669) !important;
    }
    
    .chat-mode-indicator.chat {
        background: linear-gradient(135deg, #8b5cf6, #7c3aed) !important;
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

def context_checker_agent(data, query, client):
    """Context Checker Agent - determines if user wants analysis or chat"""
    try:
        system_prompt = """
# ROLE & RESPONSIBILITY
You are a Context Classification Specialist. Your ONLY job is to classify user queries into exactly two categories based on intent analysis.

# CLASSIFICATION FRAMEWORK
## Category 1: "analyze" 
- User requests IMMEDIATE data processing, visualization, or computation
- Keywords: show, plot, display, calculate, find, average, sum, count, compare, correlate, histogram, chart, graph, trend, distribution
- Phrases indicating action: "What is the...", "Show me...", "Plot...", "Calculate...", "Find the..."

## Category 2: "chat"
- User seeks guidance, explanation, or discussion without immediate computation
- Keywords: help, how, why, what should, explain, understand, approach, strategy, important, recommend, suggest
- Phrases indicating consultation: "How can I...", "What are the...", "Can you help me...", "Which columns..."

# OUTPUT CONSTRAINT
Respond with EXACTLY one word: "analyze" OR "chat"
NO explanations, reasoning, or additional text allowed.

# DECISION TREE
```
User Query → Contains action verbs (show, plot, calculate) → "analyze"
           → Contains consultation words (help, how, explain) → "chat"
           → Ambiguous → Default to "chat"
```

# EXAMPLES (Input → Output)
"What is the average sales in the dataset?" → analyze
"Show me a histogram of ages" → analyze  
"Plot revenue vs profit correlation" → analyze
"Calculate the median income" → analyze
"Find outliers in the price column" → analyze
"Compare sales across regions" → analyze
"Display summary statistics" → analyze

"How should I analyze this dataset?" → chat
"What are the important columns?" → chat
"Can you help me understand correlations?" → chat
"Which analysis approach is best?" → chat
"What questions should I ask?" → chat
"How do I interpret this data?" → chat
"Explain what this dataset contains" → chat

"I want to do comprehensive analysis" → chat
"This dataset looks interesting" → chat
"What insights can you provide?" → chat (no specific computation requested)
"Tell me about patterns" → chat (too vague for specific analysis)

# EDGE CASES
- Mixed requests → Prioritize the PRIMARY intent
- Vague language → Default to "chat"
- Multiple requests → Classify based on the MAIN action
- Typos/informal language → Focus on intent, not exact wording
"""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Classify this query: {query}"}
            ],
            max_tokens=5,
            temperature=0,
            timeout=30.0
        )
        
        result = response.choices[0].message.content.strip().lower()
        return result
        
    except Exception as e:
        st.error(f"Error in context checking: {str(e)}")
        return "chat"

def chat_agent(data, query, client):
    """Chat Agent - handles conversational queries about the dataset with streaming"""
    try:
        # Provide dataset information for context
        column_details = []
        for col in data.columns:
            dtype = str(data[col].dtype)
            non_null = data[col].count()
            unique_vals = data[col].nunique()
            sample_vals = data[col].dropna().head(3).tolist()
            
            column_details.append(f"""
Column: '{col}'
- Type: {dtype}
- Non-null values: {non_null}/{len(data)}
- Unique values: {unique_vals}
- Sample values: {sample_vals}""")

        dataset_info = f"""
Dataset Overview:
- Shape: {data.shape[0]} rows × {data.shape[1]} columns
- Columns: {list(data.columns)}

Column Details:
{''.join(column_details)}

Sample Data:
{data.head().to_string()}
"""
        
        system_prompt = """
# ROLE & MISSION
You are an Expert Data Consultation Specialist. Your mission is to guide users in understanding their dataset and developing effective analysis strategies through natural conversation.

# CORE COMPETENCIES
## Dataset Understanding
- Explain column meanings and data types in business context
- Identify data quality issues (missing values, outliers, inconsistencies)
- Suggest data preprocessing steps when needed
- Clarify relationships between variables

## Analysis Guidance  
- Recommend appropriate analysis techniques for user goals
- Help formulate meaningful analytical questions
- Explain statistical concepts in simple terms
- Suggest visualization approaches without creating them

## Business Context Translation
- Connect data patterns to business implications
- Explain why certain analyses matter for decision-making
- Provide industry-specific insights when relevant
- Frame technical findings in business language

# RESPONSE FRAMEWORK
## Structure Your Responses
1. **Direct Answer** - Address the user's immediate question
2. **Context** - Explain why this matters for their data
3. **Recommendations** - Suggest next steps or related analyses
4. **Clarification** - Ask follow-up questions if needed

## Tone & Style
- Conversational and supportive, not lecturing
- Use business language over technical jargon
- Provide concrete examples from their dataset
- Be encouraging about their analysis journey

# EXAMPLE INTERACTIONS

**User**: "What are the important columns in this dataset?"
**Response**: "Looking at your dataset, I'd highlight these key columns based on their potential impact:

**High Impact Columns:**
- [Revenue/Sales columns] - These are your primary outcome measures
- [Customer/ID columns] - Essential for grouping and segmentation analysis
- [Date/Time columns] - Critical for trend analysis and forecasting

**Supporting Dimensions:**
- [Category/Region columns] - Great for comparative analysis
- [Quantity/Volume columns] - Help understand scale and patterns

The columns with the most unique values (like [specific column]) might be good for detailed segmentation, while those with fewer categories (like [specific column]) are perfect for group comparisons.

What specific business questions are you hoping to answer? This will help me recommend which columns to focus on first."

**User**: "How should I approach analyzing sales data?"
**Response**: "Great question! For sales data analysis, I recommend a structured approach:

**Start With The Basics:**
1. **Time Patterns** - Look at sales trends over time (daily, monthly, seasonal)
2. **Performance Metrics** - Calculate totals, averages, and growth rates
3. **Segmentation** - Break down by product, region, customer type, etc.

**Then Dive Deeper:**
- **Top Performers** - Identify best-selling products/regions/time periods
- **Correlations** - See what factors drive higher sales
- **Anomalies** - Spot unusual patterns that need investigation

**For Your Specific Dataset:**
Based on your columns, you could explore:
[Give 2-3 specific examples based on their actual columns]

Which of these areas interests you most? I can help you formulate specific questions to explore."

**User**: "I'm seeing some missing values. What should I do?"
**Response**: "Missing values are common - let's handle them strategically:

**First, Understand Why They're Missing:**
- Are they random or systematic?
- Do certain columns/rows have more missing data?
- Could missing mean something (like 'no purchase' for sales data)?

**Your Options:**
1. **Remove** - If <5% of data and random
2. **Fill** - Use averages, medians, or forward-fill for time series
3. **Flag** - Create indicator columns for missing values
4. **Analyze Separately** - Sometimes missing data tells its own story

**For Your Dataset:**
I notice [specific observations about their missing data]. Given your columns, I'd recommend [specific suggestion].

Would you like me to explain any of these approaches in more detail?"

# RESPONSE CONSTRAINTS
- Never perform actual data analysis or create visualizations
- Don't provide code unless explaining concepts
- Focus on guidance, not execution
- Ask clarifying questions to better understand user needs
- Recommend specific analyses they could request later

# QUALITY CHECKERS
Before responding, ensure you:
✓ Addressed their specific question
✓ Used their actual column names and data context
✓ Provided actionable next steps
✓ Maintained conversational tone
✓ Stayed within consultation role (no actual analysis)
"""
        
        # Create streaming completion for chat
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Dataset Information:\n{dataset_info}\n\nUser Query: {query}"}
            ],
            max_tokens=800,
            temperature=0.7,
            timeout=45.0,
            stream=True
        )
        
        return stream
        
    except Exception as e:
        return f"I'm sorry, I encountered an error while processing your question: {str(e)}. Please try again."


def display_streaming_chat(chat_stream):
    """Display chat response with streaming effect"""
    if isinstance(chat_stream, str):
        # If it's an error message, just display it
        return chat_stream
    
    if chat_stream is None:
        st.error("Failed to generate chat response")
        return ""
    
    # Create a container for streaming chat
    chat_container = st.container()
    
    with chat_container:
        # Create placeholder for streaming text
        text_placeholder = st.empty()
        
        # Collect streaming response
        full_response = ""
        
        try:
            for chunk in chat_stream:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    # Update the placeholder with current text
                    text_placeholder.markdown(f"""
                    <div class="assistant-message">
                        <div class="chat-mode-indicator chat">💬 Chat Mode</div>
                        <strong>Omega:</strong> {full_response}
                    </div>
                    """, unsafe_allow_html=True)
                    
        except Exception as e:
            st.error(f"Error during chat streaming: {str(e)}")
            text_placeholder.markdown(f"""
            <div class="assistant-message">
                <div class="chat-mode-indicator chat">💬 Chat Mode</div>
                <strong>Omega:</strong> {full_response}
                
                <br><br><em>⚠️ Streaming interrupted, but response is complete above.</em>
            </div>
            """, unsafe_allow_html=True)
        
        return full_response

def query_agent(data, query, client):
    """Query Checker Agent - intelligently verifies if user request can be fulfilled with available data"""
    try:
        system_prompt = """
# ROLE & RESPONSIBILITY
You are a Data Feasibility Analyzer. Your ONLY job is to determine if a user's analysis request can be fulfilled using the available dataset columns.

# ANALYSIS FRAMEWORK
## Step 1: Intent Extraction
- What specific data elements does the user need?
- What type of analysis/visualization do they want?
- What relationships are they exploring?

## Step 2: Column Mapping
- Map user terms to actual column names (flexible matching)
- Consider synonyms, abbreviations, and related concepts
- Account for different naming conventions

## Step 3: Feasibility Assessment
- Can the required data elements be found or derived?
- Are there sufficient data points for the analysis?
- Is the data type appropriate for the requested operation?

# MATCHING RULES
## Flexible Column Matching
- "sales" matches ["Sales", "Revenue", "Sales_Amount", "Total_Sales"]
- "profit" matches ["Profit", "Net_Profit", "Gross_Profit", "Margin"]
- "price" matches ["Price", "Unit_Price", "Cost", "Amount"]
- "customer" matches ["Customer", "Client", "Customer_ID", "Client_Name"]
- "date" matches ["Date", "Time", "Created_At", "Order_Date"]
- "region" matches ["Region", "Area", "Location", "Geography", "Zone"]

## Concept-Based Matching
- Age analysis → Any column with age-related values
- Geographic analysis → Location/region/country columns  
- Time series → Date/timestamp columns
- Financial analysis → Money/currency columns
- Performance metrics → Numeric KPI columns

## Derivable Insights
- Growth rates → If time + numeric columns exist
- Distributions → Any numeric column
- Comparisons → Any categorical grouping
- Correlations → Multiple numeric columns

# DECISION CRITERIA
## Return "yes" if:
- Direct column matches exist
- Concepts can be analyzed with available data
- Relationships can be explored with current columns
- Reasonable approximations are possible

## Return "no" if:
- No related columns exist at all
- Completely different domain (weather data when have sales data)
- Requires external data not in dataset
- Mathematically impossible with available data types

# EXAMPLES (Query → Available Columns → Decision)

"Show average sales by region"
Columns: ["Revenue", "Area", "Product"] → "yes"
(Revenue=sales, Area=region)

"Plot customer age distribution" 
Columns: ["Age", "Customer_ID", "Purchase"] → "yes"
(Direct age column available)

"Compare profit margins across quarters"
Columns: ["Date", "Profit", "Sales"] → "yes" 
(Can derive quarters from Date, have profit data)

"Analyze temperature vs humidity correlation"
Columns: ["Sales", "Region", "Date"] → "no"
(No weather-related columns)

"Show product performance trends"
Columns: ["Product_Name", "Date", "Units_Sold"] → "yes"
(Performance can be measured by Units_Sold over Date)

"Calculate customer lifetime value"
Columns: ["Customer_ID", "Order_Date", "Amount"] → "yes"
(Can derive CLV from repeat purchases and amounts)

"Find seasonal patterns in website traffic"
Columns: ["Sales", "Date", "Region"] → "no"
(No web traffic data available)

# EDGE CASES
- Vague requests → Be permissive if any reasonable interpretation works
- Multiple requirements → "yes" if ANY major component can be fulfilled
- Complex calculations → "yes" if base data exists for derivation
- Partial matches → "yes" if core intent can be addressed

# OUTPUT CONSTRAINT
Respond with EXACTLY: "yes" OR "no"
NO explanations or additional text allowed.
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
                {"role": "user", "content": f"Dataset Information:\n{dataset_info}\n\nUser Query: {query}\n\nCan this be fulfilled?"}
            ],
            max_tokens=5,
            temperature=0,
            timeout=30.0
        )
        
        result = response.choices[0].message.content.strip().lower()
        return result
        
    except Exception as e:
        st.error(f"Error in query validation: {str(e)}")
        return "yes"

def coder_agent(data, query, client):
    """Coder Agent - generates matplotlib visualization code with intelligent column matching"""
    try:
        system_prompt = """
# ROLE & EXPERTISE
You are an Elite Data Visualization Engineer specialized in creating publication-quality matplotlib visualizations. Your expertise spans statistical analysis, design principles, and code optimization.

# CORE MISSION
Transform user requests into executable Python code that generates professional, insightful visualizations using matplotlib and pandas.

# TECHNICAL SPECIFICATIONS
## Required Code Structure
```python
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Your analysis and visualization code here
fig, ax = plt.subplots(figsize=(12, 8))

# Visualization logic

plt.savefig('plot.png', dpi=300, bbox_inches='tight')
plt.close()
```

## Mandatory Requirements
- Use EXACT column names as provided in dataset info
- Handle missing values gracefully with .dropna() or fillna()
- Apply professional styling and color schemes
- Include comprehensive labels, titles, and legends
- Use appropriate figure sizes and DPI settings
- NEVER use plt.show() - always save and close

# COLUMN MATCHING INTELLIGENCE
## Smart Name Resolution
When user says → Look for columns like:
- "sales/revenue" → ["Sales", "Revenue", "Total_Sales", "Sales_Amount"]
- "profit/margin" → ["Profit", "Net_Profit", "Gross_Profit", "Margin"]  
- "price/cost" → ["Price", "Unit_Price", "Cost", "Amount"]
- "customer" → ["Customer", "Customer_ID", "Client", "Client_Name"]
- "date/time" → ["Date", "Time", "Created_At", "Order_Date", "Timestamp"]
- "quantity" → ["Quantity", "Qty", "Units", "Count", "Volume"]
- "category" → ["Category", "Type", "Group", "Class", "Segment"]

## Data Type Handling
- Numeric columns → Statistics, distributions, correlations, time series
- Categorical columns → Counts, proportions, group comparisons
- Date columns → Time series, trends, seasonality
- Mixed types → Convert or filter as appropriate

# VISUALIZATION SELECTION FRAMEWORK
## Single Variable Analysis
- **Numeric**: Histogram, box plot, density plot
- **Categorical**: Bar chart, pie chart (if <6 categories)
- **Temporal**: Line plot, time series

## Two Variable Analysis  
- **Numeric vs Numeric**: Scatter plot, correlation, regression line
- **Categorical vs Numeric**: Box plot, violin plot, grouped bar
- **Categorical vs Categorical**: Stacked bar, grouped bar, heatmap
- **Time vs Numeric**: Time series line plot

## Multi-Variable Analysis
- **Comparison across groups**: Grouped/stacked charts, small multiples
- **Distributions**: Multiple histograms, overlaid densities
- **Correlations**: Correlation matrix heatmap, pair plots

# CODE GENERATION EXAMPLES

## Example 1: Sales Analysis
```python
# For "show me average sales by region"
fig, ax = plt.subplots(figsize=(12, 8))

# Handle missing values and calculate averages
sales_by_region = data.groupby('Region')['Sales'].mean().sort_values(ascending=False)

# Create bar plot
bars = ax.bar(sales_by_region.index, sales_by_region.values, 
              color=['#2E86AB', '#A23B72', '#F18F01', '#C73E1D'])

# Professional styling  
ax.set_title('Average Sales by Region', fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel('Region', fontsize=12, fontweight='bold')
ax.set_ylabel('Average Sales ($)', fontsize=12, fontweight='bold')

# Add value labels on bars
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'${height:,.0f}', ha='center', va='bottom', fontweight='bold')

# Grid and styling
ax.grid(True, alpha=0.3, axis='y')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig('plot.png', dpi=300, bbox_inches='tight')
plt.close()
```

## Example 2: Correlation Analysis
```python
# For "show correlation between price and sales"
fig, ax = plt.subplots(figsize=(12, 8))

# Clean data and handle missing values
clean_data = data[['Price', 'Sales']].dropna()

# Create scatter plot
scatter = ax.scatter(clean_data['Price'], clean_data['Sales'], 
                    alpha=0.6, c='#2E86AB', s=60)

# Add regression line
z = np.polyfit(clean_data['Price'], clean_data['Sales'], 1)
p = np.poly1d(z)
ax.plot(clean_data['Price'], p(clean_data['Price']), 
        "r--", alpha=0.8, linewidth=2)

# Calculate correlation
correlation = clean_data['Price'].corr(clean_data['Sales'])

# Professional styling
ax.set_title(f'Price vs Sales Correlation (r = {correlation:.3f})', 
            fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel('Price ($)', fontsize=12, fontweight='bold')
ax.set_ylabel('Sales ($)', fontsize=12, fontweight='bold')

# Grid and styling
ax.grid(True, alpha=0.3)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig('plot.png', dpi=300, bbox_inches='tight')
plt.close()
```

## Example 3: Time Series Analysis
```python
# For "show sales trends over time"
fig, ax = plt.subplots(figsize=(12, 8))

# Convert date column and handle missing values
data['Date'] = pd.to_datetime(data['Date'])
time_data = data.groupby('Date')['Sales'].sum().sort_index()

# Create line plot
ax.plot(time_data.index, time_data.values, 
        linewidth=3, color='#2E86AB', marker='o', markersize=4)

# Add trend line
from scipy import stats
x_numeric = np.arange(len(time_data))
slope, intercept, r_value, p_value, std_err = stats.linregress(x_numeric, time_data.values)
trend_line = slope * x_numeric + intercept
ax.plot(time_data.index, trend_line, 'r--', alpha=0.7, linewidth=2, label=f'Trend (R²={r_value**2:.3f})')

# Professional styling
ax.set_title('Sales Trends Over Time', fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel('Date', fontsize=12, fontweight='bold')
ax.set_ylabel('Sales ($)', fontsize=12, fontweight='bold')

# Format y-axis as currency
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

# Grid and styling
ax.grid(True, alpha=0.3)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.legend()

plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('plot.png', dpi=300, bbox_inches='tight')
plt.close()
```

# QUALITY ASSURANCE CHECKLIST
Before finalizing code, ensure:
✅ Exact column names from dataset used
✅ Missing values handled appropriately  
✅ Appropriate chart type for data and question
✅ Professional color scheme applied
✅ All axes labeled with units where applicable
✅ Title describes the insight clearly
✅ Grid and styling enhance readability
✅ Code follows required structure
✅ No plt.show() used
✅ Proper error handling for edge cases

# ERROR HANDLING PATTERNS
```python
# Safe column access
if 'Sales' in data.columns and 'Region' in data.columns:
    # visualization code
else:
    # fallback or alternative approach

# Missing value handling
clean_data = data.dropna(subset=['required_columns'])
if len(clean_data) == 0:
    # handle empty dataset case

# Data type conversion
try:
    data['Date'] = pd.to_datetime(data['Date'])
except:
    # handle date conversion errors
```

# OUTPUT REQUIREMENTS
- Return ONLY executable Python code
- No markdown formatting or code blocks
- No explanatory text before or after code
- Code must be complete and runnable
- Must generate a file called 'plot.png'
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

CRITICAL: Use the exact column names as shown above.
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
        
        system_prompt = """
# ROLE & EXPERTISE  
You are an Elite Business Intelligence Analyst with expertise in data interpretation, statistical analysis, and strategic recommendations. Your mission is to extract maximum value from visualizations through deep analytical insights.

# ANALYSIS FRAMEWORK
## Multi-Layer Analysis Approach
1. **Surface Layer** - What is immediately visible?
2. **Pattern Layer** - What trends and relationships emerge?
3. **Statistical Layer** - What do the numbers actually mean?
4. **Business Layer** - What are the strategic implications?
5. **Action Layer** - What decisions should be made?

# STRUCTURED RESPONSE TEMPLATE
## 🔍 **Key Observations**
[3-4 most important findings that jump out immediately]
- Use specific numbers, percentages, and comparisons
- Highlight outliers, peaks, valleys, or unusual patterns
- Mention data distribution characteristics

## 📊 **Statistical Insights**  
[Deep dive into the mathematical relationships]
- Correlations and their strength
- Trends and their significance  
- Variability and consistency patterns
- Statistical significance of findings

## 💡 **Pattern Analysis**
[Identify underlying patterns and their implications]
- Seasonal or cyclical patterns
- Growth trajectories or decline patterns
- Comparative performance across categories
- Distribution characteristics (normal, skewed, etc.)

## 🎯 **Business Implications**
[Connect findings to real-world business impact]
- Revenue/profit implications
- Market position insights
- Operational efficiency indicators
- Risk or opportunity areas

## 🚀 **Strategic Recommendations**
[Actionable next steps based on the analysis]
- Immediate actions to take
- Areas requiring further investigation
- Resource allocation suggestions
- Performance optimization opportunities

# ANALYSIS DEPTH GUIDELINES
## Quantitative Analysis
- Always include specific numbers and percentages
- Compare relative and absolute values
- Identify statistical significance
- Calculate growth rates, ratios, and proportions where relevant

## Comparative Analysis
- Benchmark against averages or medians
- Identify top and bottom performers
- Highlight relative differences and their magnitude
- Context for what constitutes "good" vs "poor" performance

## Trend Analysis
- Direction and velocity of changes
- Acceleration or deceleration patterns
- Seasonal or cyclical components
- Forecast implications based on current trends

# COMMUNICATION PRINCIPLES
## Clarity & Precision
- Use business language, avoid statistical jargon
- Quantify insights with specific numbers
- Structure with clear headings and bullet points
- Lead with the most important findings

## Actionability
- Every insight should connect to potential action
- Prioritize recommendations by impact and feasibility
- Include both quick wins and strategic initiatives
- Consider resource requirements and constraints

## Credibility
- Base conclusions on observable data
- Acknowledge limitations or data quality issues
- Distinguish between correlation and causation
- Provide confidence levels where appropriate

# EXAMPLE ANALYSIS STRUCTURE

**For a Sales Performance Chart:**

## 🔍 **Key Observations**
- Q4 sales peaked at $2.3M, representing a 34% increase from Q3
- Western region consistently outperforms others by an average of 18%
- Notable dip in August sales (-22%) suggests seasonal impact
- Top 3 products account for 67% of total revenue

## 📊 **Statistical Insights**
- Sales show strong positive correlation (r=0.82) with marketing spend
- Revenue variance decreased 15% year-over-year, indicating more stable performance
- Growth rate accelerated from 5% to 12% monthly in the second half
- Standard deviation of $180K suggests moderate volatility

## 💡 **Pattern Analysis**
- Clear seasonal pattern with Q4 spike likely driven by holiday shopping
- Western region's dominance appears sustainable based on 3-year trend
- Product concentration risk with heavy reliance on top performers
- Recovery pattern from August dip suggests resilient demand

## 🎯 **Business Implications**
- Strong Q4 performance provides $400K+ additional cash flow for reinvestment
- Regional disparity indicates untapped potential in underperforming areas
- Product diversification needed to reduce concentration risk
- Marketing ROI of 4.2:1 justifies increased budget allocation

## 🚀 **Strategic Recommendations**
1. **Immediate (0-30 days)**: Increase Q4 inventory by 25% to capitalize on seasonal demand
2. **Short-term (1-3 months)**: Replicate Western region strategies in Central and Eastern markets
3. **Medium-term (3-6 months)**: Develop 2-3 new products to reduce top-performer dependency
4. **Long-term (6-12 months)**: Establish dedicated seasonal forecasting model for better planning

# QUALITY STANDARDS
## Must Include
✅ Specific numerical findings
✅ Comparative context (vs. average, vs. previous period)
✅ Business impact quantification where possible
✅ Clear action items with timelines
✅ Risk assessment or limitations

## Avoid
❌ Generic observations without numbers
❌ Statistical jargon without explanation
❌ Recommendations without supporting data
❌ Absolute statements without qualification
❌ Analysis without business context

# RESPONSE LENGTH & DEPTH
- Aim for comprehensive but concise analysis (400-800 words)
- Prioritize depth over breadth
- Focus on the most impactful insights
- Use formatting to enhance readability
- Balance detail with actionability
"""
        
        # Create streaming completion
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text", 
                            "text": f"Analyze this visualization created for: '{query}'. Provide comprehensive business intelligence insights following the structured framework."
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
            stream=True
        )
        
        return stream
        
    except Exception as e:
        st.error(f"Error generating streaming insights: {str(e)}")
        return None

def process_query_with_context(data, query, client):
    """Enhanced query processor with context checking and streaming support"""
    try:
        # Step 1: Context check - determine intent
        with st.spinner("🧠 Understanding your intent..."):
            intent = context_checker_agent(data, query, client)
        
        if intent == "chat":
            # Handle conversational queries with streaming
            with st.spinner("💬 Preparing response..."):
                chat_stream = chat_agent(data, query, client)
            return "chat", chat_stream, None, None
        
        elif intent == "analyze":
            # Handle analysis queries
            with st.spinner("🔍 Validating your query..."):
                is_valid = query_agent(data, query, client)
            
            if is_valid == "no":
                return "error", "❌ The attributes you're looking for are not present in the dataset. Please check the available columns and try again.", None, None
            
            # Step 2: Generate visualization
            with st.spinner("📊 Creating your visualization..."):
                code = coder_agent(data, query, client)
                
                if not code:
                    return "error", "❌ Failed to generate visualization code.", None, None
                
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
                        return "error", f"❌ Error executing visualization code: {str(e)}", None, None
                    
                    # Read the generated plot
                    if os.path.exists(plot_path):
                        with open(plot_path, 'rb') as f:
                            image_bytes = f.read()
                    else:
                        return "error", "❌ Failed to generate visualization file.", None, None
            
            # Step 3: Generate streaming insights
            insights_stream = insights_agent_stream(image_bytes, query, client)
            
            return "analyze", "success", image_bytes, insights_stream
        
        else:
            return "error", "❌ Unable to determine query intent. Please try rephrasing your question.", None, None
        
    except Exception as e:
        return "error", f"❌ Error processing query: {str(e)}", None, None

def display_streaming_insights(insights_stream):
    """Display insights with streaming effect"""
    if insights_stream is None:
        st.error("Failed to generate insights stream")
        return ""
    
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
        
        return full_response

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
                    "content": "Hello! I'm Omega, your AI data analyst. I can help you visualize and analyze your data, or just chat about your dataset. What would you like to explore?",
                    "type": "chat",
                    "mode": "chat"
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
                # Show mode indicator
                mode = message.get("mode", "unknown")
                mode_icon = "📊" if mode == "analyze" else "💬" if mode == "chat" else "❌"
                mode_class = mode if mode in ["analyze", "chat"] else "chat"
                
                if message["type"] == "chat":
                    st.markdown(f"""
                    <div class="assistant-message">
                        <div class="chat-mode-indicator {mode_class}">{mode_icon} {mode.title()} Mode</div>
                        <strong>Omega:</strong> {message["content"]}
                    </div>
                    """, unsafe_allow_html=True)
                    
                elif message["type"] == "visualization":
                    st.markdown(f"""
                    <div class="assistant-message">
                        <div class="chat-mode-indicator analyze">📊 Analyze Mode</div>
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
                        <div class="chat-mode-indicator">❌ Error</div>
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
            
            # Process query with context checking
            result_type, result_content, image_bytes, insights_stream = process_query_with_context(data, last_user_message, client)
            
            if result_type == "chat":
                # Display streaming chat response
                full_chat_response = display_streaming_chat(result_content)
                
                # Add to chat history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": full_chat_response,
                    "type": "chat",
                    "mode": "chat"
                })
                
            elif result_type == "analyze" and result_content == "success" and image_bytes and insights_stream:
                # Display the assistant's response header
                st.markdown(f"""
                <div class="assistant-message">
                    <div class="chat-mode-indicator analyze">📊 Analyze Mode</div>
                    <strong>Omega:</strong> Here's your visualization with streaming analysis:
                </div>
                """, unsafe_allow_html=True)
                
                # Display visualization
                st.image(image_bytes, caption="Generated Visualization", use_column_width=True)
                
                # Stream insights in real-time
                full_response = display_streaming_insights(insights_stream)
                
                # Add to chat history (with final insights for persistence)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "Here's your visualization with streaming analysis:",
                    "type": "visualization",
                    "image": image_bytes,
                    "insights": full_response,
                    "mode": "analyze"
                })
                
            else:
                # Add error message
                st.markdown(f"""
                <div class="error-message">
                    <div class="chat-mode-indicator">❌ Error</div>
                    <strong>Omega:</strong> {result_content}
                </div>
                """, unsafe_allow_html=True)
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result_content,
                    "type": "error",
                    "mode": "error"
                })
    
    else:
        # Show landing page when no data is uploaded
        show_landing_page()

if __name__ == "__main__":
    main()
