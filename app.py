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

# Configure Streamlit page with white theme
st.set_page_config(
    page_title="Omega - AI Data Analyst",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Force white theme and modern styling
st.markdown("""
<style>
    /* Force light theme */
    .stApp {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
    }
    
    /* Override all backgrounds to white */
    .main .block-container {
        background-color: #ffffff !important;
        padding-top: 2rem !important;
    }
    
    /* Sidebar styling */
    .css-1d391kg, .css-1lcbmhc, .css-17lntkn, section[data-testid="stSidebar"] {
        background-color: #f8fafc !important;
        border-right: 1px solid #e2e8f0 !important;
    }
    
    /* Modern typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
        background-color: #ffffff !important;
        color: #1a1a1a !important;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        padding: 3rem 2rem !important;
        border-radius: 16px !important;
        margin-bottom: 2rem !important;
        text-align: center !important;
        color: white !important;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.2) !important;
    }
    
    .main-header h1 {
        font-size: 3.5rem !important;
        font-weight: 700 !important;
        margin-bottom: 0.5rem !important;
        font-family: 'Inter', sans-serif !important;
        color: white !important;
    }
    
    .main-header p {
        font-size: 1.25rem !important;
        font-weight: 400 !important;
        opacity: 0.95 !important;
        font-family: 'Inter', sans-serif !important;
        color: white !important;
    }
    
    /* Chat interface styling */
    .chat-container {
        background-color: #ffffff !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
        margin-bottom: 1rem !important;
        border: 1px solid #e2e8f0 !important;
    }
    
    .user-message {
        background: linear-gradient(135deg, #3b82f6, #1d4ed8) !important;
        color: white !important;
        padding: 1rem 1.5rem !important;
        border-radius: 18px 18px 4px 18px !important;
        margin: 1rem 0 !important;
        margin-left: 20% !important;
        font-weight: 500 !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15) !important;
    }
    
    .assistant-message {
        background-color: #f1f5f9 !important;
        color: #1e293b !important;
        padding: 1rem 1.5rem !important;
        border-radius: 18px 18px 18px 4px !important;
        margin: 1rem 0 !important;
        margin-right: 20% !important;
        border-left: 4px solid #10b981 !important;
        font-weight: 400 !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05) !important;
    }
    
    .error-message {
        background-color: #fef2f2 !important;
        color: #dc2626 !important;
        padding: 1rem 1.5rem !important;
        border-radius: 12px !important;
        margin: 1rem 0 !important;
        border-left: 4px solid #ef4444 !important;
        font-weight: 500 !important;
    }
    
    /* Input styling */
    .stTextInput > div > div > input, .stChatInput > div > div > input {
        background-color: #ffffff !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 12px !important;
        color: #1a1a1a !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 1rem !important;
        padding: 0.75rem 1rem !important;
        transition: all 0.2s ease !important;
    }
    
    .stTextInput > div > div > input:focus, .stChatInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
        outline: none !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3) !important;
    }
    
    /* Metrics cards */
    .metric-card {
        background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%) !important;
        padding: 1.5rem !important;
        border-radius: 12px !important;
        border: 1px solid #e2e8f0 !important;
        text-align: center !important;
        color: #1e293b !important;
        font-family: 'Inter', sans-serif !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05) !important;
        transition: all 0.2s ease !important;
    }
    
    .metric-card:hover {
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1) !important;
        transform: translateY(-2px) !important;
    }
    
    .metric-card h4 {
        color: #64748b !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        margin-bottom: 0.5rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }
    
    .metric-card h2 {
        color: #1e293b !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
        margin: 0 !important;
    }
    
    /* File uploader */
    .uploadedFile {
        background-color: #f8fafc !important;
        border: 2px dashed #94a3b8 !important;
        border-radius: 12px !important;
        padding: 2rem !important;
        text-align: center !important;
        color: #475569 !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.2s ease !important;
    }
    
    .uploadedFile:hover {
        border-color: #667eea !important;
        background-color: #f1f5f9 !important;
    }
    
    /* Override Streamlit's default text colors */
    .stMarkdown, .stMarkdown p, .stText, div[data-testid="stMarkdownContainer"] p {
        color: #1e293b !important;
        font-family: 'Inter', sans-serif !important;
        line-height: 1.6 !important;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #1e293b !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
    }
    
    /* Success and info messages */
    .stSuccess {
        background-color: #f0fdf4 !important;
        border: 1px solid #22c55e !important;
        color: #15803d !important;
    }
    
    .stInfo {
        background-color: #f0f9ff !important;
        border: 1px solid #3b82f6 !important;
        color: #1d4ed8 !important;
    }
    
    .stError {
        background-color: #fef2f2 !important;
        border: 1px solid #ef4444 !important;
        color: #dc2626 !important;
    }
    
    /* Welcome section styling */
    .welcome-section {
        background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%) !important;
        padding: 3rem 2rem !important;
        border-radius: 16px !important;
        text-align: center !important;
        color: #1e293b !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05) !important;
    }
    
    .welcome-section h2 {
        color: #1e293b !important;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        margin-bottom: 1rem !important;
    }
    
    .welcome-section p {
        color: #64748b !important;
        font-size: 1.125rem !important;
        font-weight: 400 !important;
    }
    
    .feature-box {
        background-color: #ffffff !important;
        padding: 2rem !important;
        border-radius: 12px !important;
        border: 1px solid #e2e8f0 !important;
        margin: 2rem auto !important;
        max-width: 600px !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05) !important;
    }
    
    .feature-box h3 {
        color: #1e293b !important;
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        margin-bottom: 1rem !important;
    }
    
    .feature-list {
        text-align: left !important;
        color: #475569 !important;
    }
    
    .feature-list p {
        color: #475569 !important;
        margin: 0.75rem 0 !important;
        font-weight: 500 !important;
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
        border-top: 4px solid #667eea !important;
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
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize OpenAI client with better error handling
def init_openai():
    try:
        # Try multiple ways to get the API key
        api_key = None
        
        # Method 1: Streamlit secrets
        try:
            api_key = st.secrets["OPENAI_API_KEY"]
        except:
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
            api_key = st.text_input("🔑 Enter your OpenAI API Key:", type="password")
            
            if not api_key:
                st.stop()
        
        # Test the API key
        client = OpenAI(api_key=api_key)
        
        # Test connection with a simple call
        try:
            client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            st.success("✅ OpenAI API connection successful!")
        except Exception as e:
            st.error(f"❌ API key validation failed: {str(e)}")
            st.stop()
            
        return client
        
    except Exception as e:
        st.error(f"❌ Error initializing OpenAI client: {str(e)}")
        st.stop()

def query_agent(data, query, client):
    """Query Checker Agent - verifies if requested columns exist in dataset"""
    try:
        system_prompt = """
Role: You are a Query Checker Agent. Your sole job is to verify if the user's request involves columns that are present in the dataset provided.

Behavior:
- Read the user query and identify column names that may be mentioned
- Match those with the dataset's column headers
- If ALL required columns exist in the dataset, return: yes
- If ANY column is missing, return: no

Constraints:
- Your response must be exactly one word: yes or no
- No extra text, no explanation
"""
        
        dataset_info = f"Dataset columns: {list(data.columns)}\nSample data:\n{data.head().to_string()}"
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Dataset:\n{dataset_info}\n\nUser Prompt:\n{query}"}
            ],
            max_tokens=10,
            temperature=0
        )
        return response.choices[0].message.content.strip().lower()
    except Exception as e:
        st.error(f"Error in query validation: {str(e)}")
        return "no"

def coder_agent(data, query, client):
    """Coder Agent - generates matplotlib visualization code"""
    try:
        system_prompt = """
Role: You are an advanced visualization agent that writes Python code using matplotlib to generate insightful visualizations.

Constraints:
- Do not include plt.show() in the code
- End with: plt.savefig('plot.png', dpi=300, bbox_inches='tight'); plt.close()
- Use matplotlib and pandas only
- The data is available as pandas DataFrame named 'data'
- Always create a figure with: fig, ax = plt.subplots(figsize=(10, 6))
- Return ONLY executable Python code, no markdown formatting
- Handle missing values and data types appropriately
- Use clear titles, labels, and legends

Format: Return only raw Python code with proper error handling.
"""

        dataset_info = f"Dataset columns: {list(data.columns)}\nDataset shape: {data.shape}\nSample data:\n{data.head().to_string()}"
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Dataset:\n{dataset_info}\n\nUser Prompt:\n{query}"}
            ],
            max_tokens=800,
            temperature=0.3
        )
        
        code = response.choices[0].message.content.strip()
        
        # Clean code
        if code.startswith("```python"):
            code = code[9:]
        if code.startswith("```"):
            code = code[3:]
        if code.endswith("```"):
            code = code[:-3]
        
        return code.strip()
    except Exception as e:
        st.error(f"Error generating visualization code: {str(e)}")
        return None

def insights_agent(image_bytes, query, client):
    """Insights Agent - generates insights from visualization"""
    try:
        encoded_image = base64.b64encode(image_bytes).decode('utf-8')
        image_data_url = f"data:image/png;base64,{encoded_image}"
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text", 
                            "text": f"Analyze this visualization created for: '{query}'. Provide detailed insights about patterns, trends, and key findings. Structure your response with clear headings and bullet points."
                        },
                        {
                            "type": "image_url", 
                            "image_url": {"url": image_data_url}
                        }
                    ]
                }
            ],
            max_tokens=800
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        return f"Error generating insights: {str(e)}"

def process_query(data, query, client):
    """Central controller for processing user queries"""
    try:
        # Step 1: Validate query
        with st.spinner("🔍 Validating your query..."):
            is_valid = query_agent(data, query, client)
        
        if is_valid == "no":
            return "❌ The attributes you're looking for are not present in the dataset. Please check the available columns and try again.", None
        
        # Step 2: Generate visualization
        with st.spinner("📊 Creating your visualization..."):
            code = coder_agent(data, query, client)
            
            if not code:
                return "❌ Failed to generate visualization code.", None
            
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
                    return f"❌ Error executing visualization code: {str(e)}", None
                
                # Read the generated plot
                if os.path.exists(plot_path):
                    with open(plot_path, 'rb') as f:
                        image_bytes = f.read()
                else:
                    return "❌ Failed to generate visualization file.", None
        
        # Step 3: Generate insights
        with st.spinner("🧠 Analyzing insights..."):
            insights = insights_agent(image_bytes, query, client)
        
        return insights, image_bytes
        
    except Exception as e:
        return f"❌ Error processing query: {str(e)}", None

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 Omega</h1>
        <p>Multi-Agentic System for Intelligent Data Analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize OpenAI client
    client = init_openai()
    
    # Sidebar for file upload and dataset info
    with st.sidebar:
        st.markdown("### 📁 Upload Your Dataset")
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
                st.markdown("### 📊 Dataset Overview")
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
                st.markdown("### 📋 Available Columns")
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
    
    # Main chat interface
    if data is not None:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        st.markdown("### 💬 Chat with Your Data")
        
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {
                    "role": "assistant", 
                    "content": "Hello! I'm Omega, your AI data analyst. I can help you visualize and analyze your data. What would you like to explore?",
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
                        <strong>Omega:</strong> Here's your visualization and analysis:
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        st.image(message["image"], caption="Generated Visualization", use_column_width=True)
                    with col2:
                        st.markdown(message["insights"])
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
            
            # Process query
            insights, image_bytes = process_query(data, user_query, client)
            
            if image_bytes:
                # Add visualization message
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "Here's your visualization and analysis:",
                    "type": "visualization",
                    "image": image_bytes,
                    "insights": insights
                })
            else:
                # Add error message
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": insights,
                    "type": "error"
                })
            
            st.rerun()
    
    else:
        # Welcome screen
        st.markdown("""
        <div class="welcome-section">
            <h2>Welcome to Omega! 🚀</h2>
            <p>Your intelligent companion for data analysis and visualization</p>
            <div class="feature-box">
                <h3>How it works:</h3>
                <div class="feature-list">
                    <p><strong>1. Upload:</strong> Share your CSV or Excel dataset</p>
                    <p><strong>2. Chat:</strong> Ask questions about your data in natural language</p>
                    <p><strong>3. Visualize:</strong> Get intelligent charts and insights instantly</p>
                    <p><strong>4. Analyze:</strong> Receive detailed analysis and recommendations</p>
                </div>
            </div>
            <p style="color: #94a3b8; font-size: 1rem; margin-top: 2rem;">Start by uploading a dataset in the sidebar! 👈</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
