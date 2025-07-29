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
    page_title="Omega - AI Data Analyst",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern styling with black header
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
        padding-top: 2rem !important;
    }
    
    /* Sidebar styling */
    .css-1d391kg, .css-1lcbmhc, .css-17lntkn, section[data-testid="stSidebar"] {
        background-color: #f8fafc !important;
        border-right: 1px solid #e2e8f0 !important;
    }
    
    /* Base typography */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
        background-color: #ffffff !important;
        color: #1a1a1a !important;
    }
    
    /* Modern black header styling */
    .main-header {
        background: linear-gradient(135deg, #0f0f0f 0%, #1a1a1a 50%, #000000 100%) !important;
        padding: 4rem 2rem !important;
        border-radius: 20px !important;
        margin-bottom: 2rem !important;
        text-align: center !important;
        color: white !important;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3), 0 0 0 1px rgba(255, 255, 255, 0.05) !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    /* Subtle animated background pattern */
    .main-header::before {
        content: '' !important;
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        bottom: 0 !important;
        background: radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.1) 0%, transparent 50%),
                    radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.05) 0%, transparent 50%) !important;
        pointer-events: none !important;
    }
    
    .main-header h1 {
        font-size: 4.5rem !important;
        font-weight: 900 !important;
        margin-bottom: 0.5rem !important;
        font-family: 'Poppins', sans-serif !important;
        color: white !important;
        text-shadow: 0 0 30px rgba(255, 255, 255, 0.1) !important;
        letter-spacing: -0.02em !important;
        position: relative !important;
        z-index: 1 !important;
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
    }
    
    .main-header p {
        font-size: 1.4rem !important;
        font-weight: 400 !important;
        opacity: 0.9 !important;
        font-family: 'Inter', sans-serif !important;
        color: #e2e8f0 !important;
        position: relative !important;
        z-index: 1 !important;
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
    
    /* Welcome section styling */
    .welcome-section {
        background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%) !important;
        padding: 4rem 3rem !important;
        border-radius: 20px !important;
        text-align: center !important;
        color: #1e293b !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08) !important;
    }
    
    .welcome-section h2 {
        color: #1a1a1a !important;
        font-size: 3rem !important;
        font-weight: 800 !important;
        margin-bottom: 1.5rem !important;
        font-family: 'Poppins', sans-serif !important;
    }
    
    .welcome-section p {
        color: #64748b !important;
        font-size: 1.25rem !important;
        font-weight: 400 !important;
    }
    
    .feature-box {
        background-color: #ffffff !important;
        padding: 3rem !important;
        border-radius: 16px !important;
        border: 1px solid #e2e8f0 !important;
        margin: 3rem auto !important;
        max-width: 700px !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05) !important;
    }
    
    .feature-box h3 {
        color: #1a1a1a !important;
        font-size: 1.75rem !important;
        font-weight: 700 !important;
        margin-bottom: 1.5rem !important;
        font-family: 'Poppins', sans-serif !important;
    }
    
    .feature-list {
        text-align: left !important;
        color: #475569 !important;
    }
    
    .feature-list p {
        color: #475569 !important;
        margin: 1rem 0 !important;
        font-weight: 500 !important;
        font-size: 1.1rem !important;
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
</style>
""", unsafe_allow_html=True)

# Initialize OpenAI client with comprehensive diagnostics
def init_openai():
    try:
        api_key = None
        
        # Method 1: Streamlit secrets
        try:
            api_key = st.secrets.get("OPENAI_API_KEY")
            if api_key:
                st.info("🔍 Using API key from Streamlit secrets")
        except Exception:
            pass
        
        # Method 2: Environment variable
        if not api_key:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                st.info("🔍 Using API key from environment variable")
        
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
        
        # Connection diagnostics
        st.info("🔄 Testing connection to OpenAI API...")
        
        # Test basic connectivity first
        import requests
        try:
            # Test basic internet connectivity
            response = requests.get("https://httpbin.org/status/200", timeout=5)
            st.success("✅ Internet connection working")
        except Exception as e:
            st.error(f"❌ Internet connectivity issue: {str(e)}")
            st.info("Please check your internet connection or VPN settings")
            st.stop()
        
        # Test OpenAI API endpoint accessibility
        try:
            response = requests.get("https://api.openai.com/v1/models", 
                                  headers={"Authorization": f"Bearer {api_key}"}, 
                                  timeout=10)
            if response.status_code == 200:
                st.success("✅ OpenAI API endpoint accessible")
            elif response.status_code == 401:
                st.error("❌ Invalid API key - Authentication failed")
                st.stop()
            elif response.status_code == 429:
                st.error("❌ Rate limit exceeded")
                st.stop()
            else:
                st.warning(f"⚠️ API responded with status code: {response.status_code}")
        except requests.exceptions.Timeout:
            st.error("❌ Connection timeout to OpenAI API")
            st.info("This could be due to:")
            st.markdown("""
            - Corporate firewall blocking OpenAI
            - VPN interference
            - Regional restrictions
            - Network congestion
            """)
            st.stop()
        except Exception as e:
            st.error(f"❌ Connection error: {str(e)}")
            st.stop()
        
        # Initialize OpenAI client with progressive timeout strategy
        try:
            client = OpenAI(
                api_key=api_key,
                timeout=60.0,  # Increased timeout
                max_retries=0   # Disable retries for clearer error messages
            )
            
            # Test with a very simple call
            st.info("🧪 Testing OpenAI client with minimal request...")
            
            test_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=1,
                temperature=0
            )
            
            if test_response and test_response.choices:
                st.success("✅ OpenAI API connection successful!")
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
            
            # Add debug info expander
            with st.expander("🔍 Debug Information"):
                st.code(f"""
Error Type: {type(e).__name__}
Error Message: {str(e)}
API Key Format: {'Valid (sk-...)' if api_key.startswith('sk-') else 'Invalid'}
API Key Length: {len(api_key)} characters
""")
            
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
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Dataset Information:\n{dataset_info}\n\nUser Query: {query}\n\nCan this query be fulfilled with the available data?"}
            ],
            max_tokens=5,
            temperature=0,
            timeout=15.0
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
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"{dataset_info}\n\nUser Request: {query}\n\nGenerate visualization code:"}
            ],
            max_tokens=1200,
            temperature=0.2,
            timeout=25.0
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
            max_tokens=1000,
            timeout=25.0
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
    # Modern black header
    st.markdown("""
    <div class="main-header">
        <h1>Omega</h1>
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
            <h2>Welcome to Omega! </h2>
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
