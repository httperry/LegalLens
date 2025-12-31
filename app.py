import streamlit as st
import google.generativeai as genai
from PIL import Image
import PyPDF2
import io
import json
import re

import copy

# --- Page Config ---
st.set_page_config(
    page_title="LegalLens",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Google Material Icons & Fonts CDN ---
st.markdown('''
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet" />
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
.material-symbols-outlined {
    font-variation-settings: 'FILL' 1, 'wght' 500, 'GRAD' 0, 'opsz' 24;
    vertical-align: middle;
}
</style>
''', unsafe_allow_html=True)

# --- Custom CSS ---
st.markdown("""
<style>
    * { font-family: 'Inter', sans-serif; }
    
    :root {
        --primary: #6366f1;
        --primary-light: #818cf8;
        --success: #10b981;
        --danger: #ef4444;
        --warning: #f59e0b;
    }
    
    /* Remove top padding from main container to let navbar touch top */
    .block-container {
        padding-top: 3rem !important; /* Added margin as requested */
        padding-bottom: 1rem !important;
    }
    
    /* Custom Top Navbar */
    .navbar {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
        padding: 1rem 2rem;
        margin: -3rem -1rem 2rem -1rem; /* Adjusted negative margin to match new padding */
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-radius: 0 0 1rem 1rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    }
    
    .navbar-brand {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: white;
        font-size: 1.5rem;
        font-weight: 700;
    }
    
    .navbar-brand .material-symbols-outlined {
        font-size: 2rem;
        color: #a5b4fc;
    }
    
    .navbar-tagline {
        color: #a5b4fc;
        font-size: 0.85rem;
        font-weight: 400;
    }
    
    .navbar-powered {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: #c7d2fe;
        font-size: 0.8rem;
    }
    
    .navbar-powered img { height: 20px; }
    
    .disclaimer-banner {
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        margin-bottom: 1rem;
        font-size: 0.8rem;
        color: #fca5a5;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .disclaimer-banner .material-symbols-outlined {
        color: #f87171;
        font-size: 1.1rem;
    }
    
    .section-title {
        color: #4f46e5; /* Darker indigo for better light mode contrast */
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .section-title .material-symbols-outlined { font-size: 1.2rem; }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: transparent;
        padding: 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        font-weight: 500;
        font-size: 0.85rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        color: white !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        border: none !important;
        border-radius: 0.75rem !important;
        padding: 0.6rem 1.5rem !important;
        font-weight: 600 !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4);
    }
    
    [data-testid="stFileUploader"] {
        background: rgba(99, 102, 241, 0.03);
        border: 2px dashed rgba(99, 102, 241, 0.25);
        border-radius: 0.75rem;
        padding: 0.5rem;
    }
    
    .stTextArea textarea {
        background: rgba(99, 102, 241, 0.03) !important;
        border: 1px solid rgba(99, 102, 241, 0.2) !important;
        border-radius: 0.5rem !important;
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e1b4b 0%, #312e81 100%) !important;
        padding-top: 1rem;
    }
    
    [data-testid="stSidebar"] * { color: #e0e7ff !important; }
    
    [data-testid="stSidebar"] h3 { color: #a5b4fc !important; font-size: 0.9rem !important; }
    
    [data-testid="stSidebar"] [data-testid="stAlert"] {
        background: rgba(99, 102, 241, 0.2) !important;
        border: 1px solid rgba(165, 180, 252, 0.3) !important;
    }
    
    /* Main content column - no sticky on any nested elements */
    [data-testid="stColumn"]:first-child,
    [data-testid="stColumn"]:first-child [data-testid="stColumn"] {
        position: relative !important;
    }
    [data-testid="stColumn"]:first-child > div,
    [data-testid="stColumn"]:first-child [data-testid="stColumn"] > div {
        position: relative !important;
    }
    
    /* Chat Panel - Only the OUTER right column of the main layout */
    .block-container > div > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:last-child {
        background: rgba(30, 27, 75, 0.95);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 1rem;
        padding: 1.25rem !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        position: sticky;
        top: 5rem;
        height: fit-content;
        max-height: calc(100vh - 6rem);
        overflow-y: auto;
        overflow-x: hidden;
    }
    .block-container > div > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:last-child::-webkit-scrollbar { width: 4px; }
    .block-container > div > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:last-child::-webkit-scrollbar-thumb { background: #6366f1; border-radius: 4px; }
    
    .chat-panel-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: #a5b4fc;
        font-weight: 700;
        font-size: 1.1rem;
        margin-bottom: 0.75rem;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid rgba(99, 102, 241, 0.3);
    }
    .chat-panel-header .material-symbols-outlined {
        font-size: 1.3rem;
        color: #818cf8;
    }
    .chat-welcome {
        text-align: center;
        padding: 1.5rem 1rem;
        color: #94a3b8;
    }
    .chat-welcome .material-symbols-outlined {
        font-size: 2.5rem;
        color: #6366f1;
        margin-bottom: 0.5rem;
    }
    .chat-welcome h4 {
        color: #a5b4fc;
        font-size: 0.95rem;
        margin: 0.5rem 0;
    }
    .chat-welcome p {
        font-size: 0.8rem;
        margin: 0;
        line-height: 1.4;
        color: #94a3b8;
    }
    .doc-ready-badge {
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid rgba(16, 185, 129, 0.4);
        border-radius: 0.5rem;
        padding: 0.75rem;
        margin-top: 0.5rem;
    }
    .doc-ready-badge .badge-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: #10b981;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .doc-ready-badge p {
        font-size: 0.75rem;
        color: #94a3b8;
        margin: 0.25rem 0 0 0;
    }
    .chat-messages-container {
        max-height: 400px;
        overflow-y: auto;
        padding-right: 0.5rem;
        margin-bottom: 1rem;
    }
    .chat-messages-container::-webkit-scrollbar { width: 4px; }
    .chat-messages-container::-webkit-scrollbar-thumb { background: #6366f1; border-radius: 4px; }
    
    /* Chat input styling for dark panel - only outer chat column */
    .block-container > div > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:last-child [data-testid="stChatInput"] {
        background: rgba(99, 102, 241, 0.1) !important;
        border: 1px solid rgba(99, 102, 241, 0.3) !important;
        border-radius: 0.75rem !important;
    }
    .block-container > div > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:last-child [data-testid="stChatInput"] textarea {
        color: #e0e7ff !important;
    }
    
    /* Suggestion buttons in chat panel - only outer chat column */
    .block-container > div > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:last-child .stButton > button {
        background: rgba(99, 102, 241, 0.2) !important;
        border: 1px solid rgba(99, 102, 241, 0.4) !important;
        color: #c7d2fe !important;
        box-shadow: none !important;
        font-size: 0.8rem !important;
        padding: 0.5rem 1rem !important;
    }
    .block-container > div > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:last-child .stButton > button:hover {
        background: rgba(99, 102, 241, 0.35) !important;
        transform: none !important;
    }
    
    /* Small clear button in chat header */
    .block-container > div > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:last-child [data-testid="stHorizontalBlock"] .stButton > button {
        background: transparent !important;
        border: none !important;
        padding: 0.25rem 0.5rem !important;
        min-height: auto !important;
        font-size: 1rem !important;
        opacity: 0.6;
    }
    .block-container > div > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:last-child [data-testid="stHorizontalBlock"] .stButton > button:hover {
        opacity: 1;
        background: rgba(239, 68, 68, 0.2) !important;
    }
    
    /* Chat Bubbles */
    .chat-bubble {
        padding: 10px 14px;
        border-radius: 12px;
        margin-bottom: 8px;
        font-size: 0.85rem;
        line-height: 1.5;
        word-wrap: break-word;
    }
    .user-bubble {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        margin-left: 20%;
        border-bottom-right-radius: 4px;
    }
    .ai-bubble {
        background: rgba(99, 102, 241, 0.15);
        color: #e0e7ff;
        margin-right: 20%;
        border-bottom-left-radius: 4px;
        border: 1px solid rgba(99, 102, 241, 0.3);
    }
    .ai-bubble strong {
        color: #a5b4fc;
        font-size: 0.75rem;
    }

    /* TL;DR Hero */
    .tldr-hero {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%);
        border-radius: 1rem;
        padding: 1.25rem 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 30px rgba(99, 102, 241, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .tldr-hero::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 100%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 50%);
    }
    
    .tldr-label {
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        background: rgba(255,255,255,0.2);
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 1rem;
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }
    
    .tldr-headline {
        color: white;
        font-size: 1.25rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .tldr-text {
        font-size: 0.95rem;
        font-weight: 400;
        color: rgba(255,255,255,0.95);
        line-height: 1.5;
        margin: 0;
    }
    
    /* Risk Card */
    .risk-card {
        border-radius: 0.75rem;
        padding: 1rem;
        text-align: center;
        height: 100%;
    }
    
    .risk-low { background: rgba(16, 185, 129, 0.1); border: 2px solid #10b981; }
    .risk-medium { background: rgba(245, 158, 11, 0.1); border: 2px solid #f59e0b; }
    .risk-high { background: rgba(239, 68, 68, 0.1); border: 2px solid #ef4444; }
    
    .risk-badge {
        font-size: 1.1rem;
        font-weight: 800;
        margin-bottom: 0.4rem;
    }
    
    .risk-low .risk-badge { color: #10b981; }
    .risk-medium .risk-badge { color: #f59e0b; }
    .risk-high .risk-badge { color: #ef4444; }
    
    .risk-text { font-size: 0.8rem; line-height: 1.4; margin: 0; }
    
    /* Cards */
    .card {
        background: rgba(99, 102, 241, 0.05);
        border: 1px solid rgba(99, 102, 241, 0.15);
        border-radius: 0.75rem;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .card-header {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        font-weight: 600;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }
    
    .card-header .material-symbols-outlined { font-size: 1.1rem; }
    
    .card-purple .card-header { color: #7c3aed; /* Darker purple for light mode */ }
    .card-red { background: rgba(239, 68, 68, 0.05); border-color: rgba(239, 68, 68, 0.2); }
    .card-red .card-header { color: #dc2626; /* Darker red */ }
    .card-green { background: rgba(16, 185, 129, 0.05); border-color: rgba(16, 185, 129, 0.2); }
    .card-green .card-header { color: #059669; /* Darker green */ }
    .card-amber { background: rgba(251, 191, 36, 0.05); border-color: rgba(251, 191, 36, 0.2); }
    .card-amber .card-header { color: #d97706; /* Darker amber */ }
    
    .card-content { font-size: 0.85rem; line-height: 1.5; }
    .card-content p { margin: 0.2rem 0; }
    .card-content ul { margin: 0; padding-left: 1.1rem; }
    .card-content li { margin: 0.4rem 0; }
    
    /* Terms Table */
    .terms-table { width: 100%; border-collapse: collapse; margin-top: 0.5rem; }
    .terms-table th {
        background: rgba(99, 102, 241, 0.1);
        padding: 0.5rem 0.75rem;
        text-align: left;
        font-size: 0.75rem;
        font-weight: 600;
        color: #7c3aed; /* Darker purple */
    }
    .terms-table td {
        padding: 0.5rem 0.75rem;
        border-bottom: 1px solid rgba(99, 102, 241, 0.1);
        font-size: 0.8rem;
    }
    
    /* Footer */
    .footer {
        background: rgba(30, 27, 75, 0.05); /* Lighter background for light mode compatibility */
        border-top: 1px solid rgba(99, 102, 241, 0.2);
        padding: 1rem;
        margin-top: 3rem;
        text-align: center;
        color: #64748b; /* Darker text */
    }
        /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease-out forwards;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    .translating {
        animation: pulse 1.5s infinite;
        border: 2px solid #a78bfa !important;
        transition: all 0.3s ease;
    }
    
    /* AI Loading Animation */
    .ai-loading {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 2rem;
        text-align: center;
    }
    .ai-loading-icon {
        font-size: 3rem;
        color: #6366f1;
        animation: bounce 1s infinite;
    }
    .ai-loading-text {
        color: #a5b4fc;
        font-size: 1rem;
        font-weight: 600;
        margin-top: 1rem;
    }
    .ai-loading-subtext {
        color: #64748b;
        font-size: 0.8rem;
        margin-top: 0.5rem;
    }
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    /* Typing indicator for chat */
    .typing-indicator {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 12px 16px;
        background: rgba(99, 102, 241, 0.15);
        border-radius: 12px;
        border-bottom-left-radius: 4px;
        margin-right: 20%;
        border: 1px solid rgba(99, 102, 241, 0.3);
    }
    .typing-indicator span {
        color: #a5b4fc;
        font-size: 0.8rem;
    }
    .typing-dots {
        display: flex;
        gap: 4px;
    }
    .typing-dots div {
        width: 8px;
        height: 8px;
        background: #6366f1;
        border-radius: 50%;
        animation: typingBounce 1.4s infinite ease-in-out;
    }
    .typing-dots div:nth-child(1) { animation-delay: 0s; }
    .typing-dots div:nth-child(2) { animation-delay: 0.2s; }
    .typing-dots div:nth-child(3) { animation-delay: 0.4s; }
    @keyframes typingBounce {
        0%, 80%, 100% { transform: scale(0.6); opacity: 0.5; }
        40% { transform: scale(1); opacity: 1; }
    }
    
    /* Progress bar for analysis */
    .analysis-progress {
        background: rgba(99, 102, 241, 0.1);
        border-radius: 1rem;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid rgba(99, 102, 241, 0.2);
    }
    .progress-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1rem;
    }
    .progress-icon {
        font-size: 1.5rem;
        color: #6366f1;
        animation: spin 2s linear infinite;
    }
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    .progress-title {
        color: #a5b4fc;
        font-weight: 600;
        font-size: 1rem;
    }
    .progress-bar-container {
        background: rgba(99, 102, 241, 0.2);
        border-radius: 0.5rem;
        height: 8px;
        overflow: hidden;
        margin-bottom: 0.75rem;
    }
    .progress-bar-fill {
        height: 100%;
        background: linear-gradient(90deg, #6366f1, #8b5cf6, #6366f1);
        background-size: 200% 100%;
        animation: progressShimmer 1.5s infinite linear;
        border-radius: 0.5rem;
    }
    @keyframes progressShimmer {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }
    .progress-steps {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
    }
    .progress-step {
        font-size: 0.75rem;
        color: #64748b;
        background: rgba(99, 102, 241, 0.1);
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
    }
    .progress-step.active {
        color: #a5b4fc;
        background: rgba(99, 102, 241, 0.3);
    }
    
    #MainMenu, footer { visibility: hidden; }
    
    /* Mobile Optimization */
    @media (max-width: 768px) {
        .block-container { padding-top: 1rem !important; }
        .navbar { 
            flex-direction: column; 
            align-items: flex-start; 
            gap: 0.5rem;
            padding: 1rem;
        }
        .navbar-brand { font-size: 1.2rem; }
        .tldr-headline { font-size: 1.1rem; }
        .risk-badge { font-size: 1rem; }
        .card-header { font-size: 0.85rem; }
        .stButton > button { width: 100%; }
    }
</style>
""", unsafe_allow_html=True)

# --- Languages for Translation ---
LANGUAGES = {
    "English": "en", "Hindi": "hi", "Spanish": "es", "French": "fr",
    "German": "de", "Chinese (Simplified)": "zh-CN", "Japanese": "ja",
    "Korean": "ko", "Portuguese": "pt", "Arabic": "ar", "Russian": "ru",
    "Italian": "it", "Dutch": "nl", "Tamil": "ta", "Telugu": "te",
    "Marathi": "mr", "Bengali": "bn", "Gujarati": "gu"
}

# --- Navbar & Header ---
# Remove default sidebar and create a top header area
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("Configuration Error: GEMINI_API_KEY not found in secrets.toml")
    st.stop()

# Top Header Layout
header_c1, header_c2, header_c3 = st.columns([2, 2, 1], gap="medium")

with header_c1:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 1rem; padding: 0.5rem 0;">
        <div style="display: flex; align-items: center; gap: 0.5rem; color: #6366f1; font-size: 1.8rem; font-weight: 700;">
            <span class="material-symbols-outlined" style="font-size: 2.2rem;">policy</span>
            LegalLens
        </div>
        <div style="background: rgba(99, 102, 241, 0.1); padding: 0.25rem 0.75rem; border-radius: 1rem; font-size: 0.75rem; color: #6366f1; font-weight: 600; letter-spacing: 0.05em;">
            AI CONTRACT ANALYST
        </div>
    </div>
    """, unsafe_allow_html=True)

with header_c2:
    st.markdown("""
    <div style="display: flex; align-items: center; justify-content: center; width: 100%; padding: 0.3rem 0;">
        <div style="display: inline-flex; align-items: center; gap: 0.5rem; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); padding: 0.4rem 1rem; border-radius: 2rem; border: 1px solid rgba(66, 133, 244, 0.3);">
            <span style="font-size: 0.75rem; color: #9ca3af;">Powered by</span>
            <img src="https://www.gstatic.com/lamda/images/gemini_sparkle_v002_d4735304ff6292a690345.svg" alt="Gemini" style="height: 22px;">
            <span style="font-size: 0.95rem; font-weight: 600; background: linear-gradient(90deg, #4285f4, #ea4335, #fbbc04, #34a853); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">Gemini 2.5 Flash</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with header_c3:
    target_language = st.selectbox(
        "Output Language",
        options=list(LANGUAGES.keys()),
        index=0,
        label_visibility="visible",
        key="target_language"
    )

st.markdown("---")

# --- Helper Functions ---
def extract_pdf_text(uploaded_file):
    """Extract text from uploaded PDF file."""
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text.strip()
    except Exception as e:
        return f"Error extracting PDF: {str(e)}"

def analyze_contract(content, input_type, api_key, target_language="English"):
    """Send content to Gemini for analysis using CO-STAR framework prompts."""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Get prompts from session state (CO-STAR framework)
        system_instructions = st.session_state.get('system_prompt', '')
        analysis_instructions = st.session_state.get('analysis_prompt', '')
        
        # Language instruction - put at the END for maximum impact
        language_instruction = ""
        if target_language != "English":
            language_instruction = f"""

⚠️ LANGUAGE REQUIREMENT - THIS IS MANDATORY ⚠️
You MUST write ALL text values in {target_language}.
- JSON keys stay in English (tldr_headline, risk_level, etc.)
- ALL values MUST be in {target_language}
- Headlines: in {target_language}
- Explanations: in {target_language}
- Summaries: in {target_language}
- Red flag titles and descriptions: in {target_language}
- Good parts titles and descriptions: in {target_language}
- Key terms and meanings: in {target_language}
- Questions: in {target_language}
DO NOT respond in English. Respond in {target_language}."""
        
        analysis_prompt = f"""{system_instructions}

IMPORTANT: You provide educational information only. Your analysis is NOT legal advice.

{analysis_instructions}

Respond with ONLY valid JSON (no markdown, no code blocks, no extra text).

Use this EXACT JSON structure:

{{
    "tldr_headline": "A catchy 3-6 word headline (e.g., 'Risky Employment Contract' or 'Standard Rental Agreement')",
    "tldr_explanation": "A detailed 3-4 sentence explanation in very simple everyday language that anyone can understand. Explain what the person is actually agreeing to as if explaining to a friend. Be specific about key commitments, money involved, time periods, and what happens if they break the agreement. Use conversational tone.",
    "risk_level": "LOW" or "MEDIUM" or "HIGH",
    "risk_explanation": "One clear sentence explaining why this risk level",
    "legitimacy_score": "Integer 0-100 representing how legitimate/professional the document looks (100=Very Legitimate, 0=Likely Scam)",
    "scam_risk": "LOW" or "MEDIUM" or "HIGH",
    "document_type": "Type of document (e.g., Employment Contract, Rental Agreement)",
    "parties_summary": "Who is involved, explained simply",
    "plain_summary": "A 3-4 sentence summary a teenager could understand. What does signing actually mean?",
    "red_flags": [
        {{"title": "Short issue name", "quote": "Brief quote", "why_bad": "Why this hurts the signer"}}
    ],
    "good_parts": [
        {{"title": "Short benefit name", "why_good": "Why this helps the signer"}}
    ],
    "key_terms": [
        {{"term": "Legal term", "meaning": "Simple 5-10 word definition"}}
    ],
    "questions": ["Simple question to ask before signing"]
}}

Additional Rules:
- Keep explanations SHORT and SIMPLE
- Use everyday language, avoid legal jargon
- Be specific about money, time periods, obligations
- Focus on what matters most to the person signing
- Limit: 5 red flags, 3 good parts, 5 key terms, 4 questions
- Make the tldr_explanation detailed and helpful - this is the most important part
- If quoting multiple parts, combine them into a SINGLE string. Do NOT use "quote1" and "quote2".
{language_instruction}
Respond with ONLY the JSON object. No other text."""
        
        # Show animated loading state
        loading_placeholder = st.empty()
        loading_placeholder.markdown('''
        <div class="analysis-progress">
            <div class="progress-header">
                <span class="material-symbols-outlined progress-icon">psychology</span>
                <span class="progress-title">Analyzing your document...</span>
            </div>
            <div class="progress-bar-container">
                <div class="progress-bar-fill" style="width: 100%;"></div>
            </div>
            <div class="progress-steps">
                <span class="progress-step active">Reading document</span>
                <span class="progress-step active">Identifying clauses</span>
                <span class="progress-step active">Assessing risks</span>
                <span class="progress-step active">Generating summary</span>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        if input_type == "image":
            response = model.generate_content([analysis_prompt, content])
        elif input_type == "pdf":
            # Send PDF directly to Gemini (native PDF support)
            response = model.generate_content([analysis_prompt, content])
        else:
            full_prompt = analysis_prompt + f"\n\n---\n\nDOCUMENT TO ANALYZE:\n\n{content}"
            response = model.generate_content(full_prompt)
        
        # Clear the loading animation
        loading_placeholder.empty()
        
        return response.text
            
    except Exception as e:
        error_msg = str(e)
        if "API_KEY" in error_msg.upper() or "INVALID" in error_msg.upper():
            return '{"error": "Invalid API Key. Please check your key and try again."}'
        elif "QUOTA" in error_msg.upper():
            return '{"error": "API quota exceeded. Please try again later."}'
        else:
            return f'{{"error": "Analysis failed: {error_msg}"}}'

def render_tldr(data, extra_class=""):
    headline = data.get('tldr_headline', data.get('tldr', 'Analysis Complete'))
    explanation = data.get('tldr_explanation', data.get('plain_summary', 'Review the details below.'))
    return f"""
    <div class="tldr-hero fade-in {extra_class}">
        <div class="tldr-label">
            <span class="material-symbols-outlined" style="font-size: 0.9rem;">bolt</span>
            Quick Summary
        </div>
        <div class="tldr-headline">{headline}</div>
        <p class="tldr-text">{explanation}</p>
    </div>
    """

def render_risk_row(data, extra_class=""):
    risk = data.get('risk_level', 'MEDIUM').upper()
    risk_class = f"risk-{risk.lower()}"
    risk_icon = "check_circle" if risk == "LOW" else "warning" if risk == "MEDIUM" else "dangerous"
    
    risk_html = f"""
    <div class="risk-card {risk_class} fade-in {extra_class}">
        <div class="risk-badge">
            <span class="material-symbols-outlined" style="font-size: 1.2rem; vertical-align: middle;">{risk_icon}</span>
            {risk} RISK
        </div>
        <p class="risk-text">{data.get('risk_explanation', '')}</p>
    </div>
    """
    
    doc_html = f"""
    <div class="card card-purple fade-in {extra_class}" style="height: 100%;">
        <div class="card-header">
            <span class="material-symbols-outlined">description</span>
            Document Info
        </div>
        <div class="card-content">
            <p><strong>Type:</strong> {data.get('document_type', 'Unknown')}</p>
            <p><strong>Parties:</strong> {data.get('parties_summary', data.get('parties', 'Unknown'))}</p>
        </div>
    </div>
    """
    return risk_html, doc_html

def render_legitimacy_card(data, extra_class=""):
    score = data.get('legitimacy_score', 50)
    scam_risk = data.get('scam_risk', 'MEDIUM')
    
    color = "#10b981" # Green
    if score < 40: color = "#ef4444" # Red
    elif score < 70: color = "#f59e0b" # Amber
    
    return f"""
    <div class="card fade-in {extra_class}" style="border-left: 4px solid {color};">
        <div class="card-header" style="color: {color};">
            <span class="material-symbols-outlined">verified_user</span>
            Legitimacy Check
        </div>
        <div class="card-content">
            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 0.5rem;">
                <div style="font-size: 2rem; font-weight: 800; color: {color};">{score}%</div>
                <div style="font-size: 0.9rem; opacity: 0.8;">Legitimacy Score</div>
            </div>
            <p><strong>Scam Risk:</strong> <span style="color: {color}; font-weight: 700;">{scam_risk}</span></p>
            <p style="font-size: 0.8rem; opacity: 0.7;">Based on document structure, language, and standard clauses.</p>
        </div>
    </div>
    """

def render_plain_summary(data, extra_class=""):
    plain_summary = data.get('plain_summary', '')
    if plain_summary:
        return f"""
        <div class="card card-purple fade-in {extra_class}">
            <div class="card-header">
                <span class="material-symbols-outlined">menu_book</span>
                What This Means For You
            </div>
            <div class="card-content">
                <p>{plain_summary}</p>
            </div>
        </div>
        """
    return ""

def render_flags_and_good(data, extra_class=""):
    # Red Flags
    red_flags = data.get('red_flags', [])
    flags_html_content = ""
    if red_flags:
        list_items = ""
        for flag in red_flags[:5]:
            if isinstance(flag, dict):
                title = flag.get('title', 'Issue')
                quote = flag.get('quote', '')
                why_bad = flag.get('why_bad', flag.get('explanation', ''))
                quote_html = f'<br><em style="color: #94a3b8; font-size: 0.75rem;">"{quote}"</em>' if quote else ''
                list_items += f'<li><strong>{title}</strong>{quote_html}<br><span style="font-size: 0.8rem;">{why_bad}</span></li>'
        
        flags_html_content = f"""
        <div class="card card-red fade-in {extra_class}">
            <div class="card-header">
                <span class="material-symbols-outlined">flag</span>
                Watch Out For
            </div>
            <div class="card-content">
                <ul>{list_items}</ul>
            </div>
        </div>
        """

    # Good Parts
    good_parts = data.get('good_parts', data.get('positive_clauses', []))
    good_html_content = ""
    if good_parts:
        list_items = ""
        for part in good_parts[:3]:
            if isinstance(part, dict):
                title = part.get('title', 'Benefit')
                why_good = part.get('why_good', part.get('explanation', ''))
                list_items += f'<li><strong>{title}</strong><br><span style="font-size: 0.8rem;">{why_good}</span></li>'
        
        good_html_content = f"""
        <div class="card card-green fade-in {extra_class}">
            <div class="card-header">
                <span class="material-symbols-outlined">thumb_up</span>
                Good Parts
            </div>
            <div class="card-content">
                <ul>{list_items}</ul>
            </div>
        </div>
        """
    return flags_html_content, good_html_content

def render_terms(data, extra_class=""):
    terms = data.get('key_terms', [])
    if terms:
        terms_rows = ""
        for t in terms[:5]:
            if isinstance(t, dict):
                terms_rows += f'<tr><td><strong>{t.get("term", "")}</strong></td><td>{t.get("meaning", "")}</td></tr>'
        
        return f"""
        <div class="card card-purple fade-in {extra_class}">
            <div class="card-header">
                <span class="material-symbols-outlined">dictionary</span>
                Key Terms Explained
            </div>
            <table class="terms-table">
                <thead><tr><th>Term</th><th>What It Means</th></tr></thead>
                <tbody>{terms_rows}</tbody>
            </table>
        </div>
        """
    return ""

def render_questions(data, extra_class=""):
    questions = data.get('questions', data.get('questions_to_ask', []))
    if questions:
        q_html = "".join([f'<li>{q}</li>' for q in questions[:4] if isinstance(q, str)])
        return f"""
        <div class="card card-amber fade-in {extra_class}">
            <div class="card-header">
                <span class="material-symbols-outlined">help</span>
                Ask Before You Sign
            </div>
            <div class="card-content">
                <ul>{q_html}</ul>
            </div>
        </div>
        """
    return ""

def display_results(data):
    """Parse and display the analysis results in beautiful cards. Returns placeholders."""
    placeholders = {}
    
    try:
        # Check for error
        if "error" in data:
            st.error(f"Error: {data['error']}")
            return {}
        
        # Create two main columns for the results to ensure tight vertical stacking
        # Left Column: Summary, Details, Flags (Heavier text)
        # Right Column: Scores, Metadata, Terms (Quick info)
        c1, c2 = st.columns([1.6, 1], gap="medium")
        
        with c1:
            # 1. TL;DR
            placeholders['tldr'] = st.empty()
            placeholders['tldr'].markdown(render_tldr(data), unsafe_allow_html=True)
            
            # 2. Plain Summary
            placeholders['summary'] = st.empty()
            placeholders['summary'].markdown(render_plain_summary(data), unsafe_allow_html=True)
            
            # 3. Red Flags
            placeholders['flags'] = st.empty()
            flags_html, good_html = render_flags_and_good(data)
            if flags_html: placeholders['flags'].markdown(flags_html, unsafe_allow_html=True)
            
            # 4. Good Parts
            placeholders['good'] = st.empty()
            if good_html: placeholders['good'].markdown(good_html, unsafe_allow_html=True)

        with c2:
            # 1. Legitimacy Score (Top Right as requested)
            placeholders['legitimacy'] = st.empty()
            legit_html = render_legitimacy_card(data)
            placeholders['legitimacy'].markdown(legit_html, unsafe_allow_html=True)
            
            # 2. Risk Level
            placeholders['risk'] = st.empty()
            risk_html, doc_html = render_risk_row(data)
            placeholders['risk'].markdown(risk_html, unsafe_allow_html=True)
            
            # 3. Document Info
            placeholders['doc_info'] = st.empty()
            placeholders['doc_info'].markdown(doc_html, unsafe_allow_html=True)
            
            # 4. Key Terms
            placeholders['terms'] = st.empty()
            placeholders['terms'].markdown(render_terms(data), unsafe_allow_html=True)
            
            # 5. Questions
            placeholders['questions'] = st.empty()
            placeholders['questions'].markdown(render_questions(data), unsafe_allow_html=True)
        
        return placeholders
        
    except Exception as e:
        st.error(f"Failed to display results: {str(e)}")
        return {}

# --- CO-STAR Framework Prompts (Best Practices) ---
# Initialize default prompts using CO-STAR framework
if 'system_prompt' not in st.session_state:
    st.session_state.system_prompt = """You are LegalLens, an expert legal document analyzer specializing in making complex legal language accessible to everyday people.

**CONTEXT:** Users upload legal documents (contracts, agreements, terms of service) seeking to understand what they're signing without expensive lawyer consultations.

**OBJECTIVE:** Analyze legal documents and provide clear, actionable insights that help users:
- Understand what they're agreeing to in plain language
- Identify potential risks and red flags
- Recognize beneficial clauses
- Know what questions to ask before signing

**STYLE:** Communicate like a knowledgeable friend who happens to be a lawyer - warm, approachable, but precise. Use analogies and real-world examples.

**TONE:** Supportive and empowering. Never condescending. Acknowledge that legal documents are genuinely confusing.

**AUDIENCE:** Non-lawyers aged 18-65 who need to make informed decisions about legal documents. Assume no legal background.

**RESPONSE FORMAT:** Structured JSON with clear sections for quick scanning. Prioritize the most important information first."""

if 'analysis_prompt' not in st.session_state:
    st.session_state.analysis_prompt = """Analyze the provided legal document following this structure:

1. **TL;DR HEADLINE** (3-6 words): Catchy summary capturing the document's essence
2. **TL;DR EXPLANATION** (3-4 sentences): Plain-language explanation of what signing means
3. **RISK ASSESSMENT**: Overall risk level with clear justification
4. **LEGITIMACY CHECK**: Score 0-100 with scam risk indicator
5. **RED FLAGS**: Issues that could harm the signer (max 5)
6. **GOOD PARTS**: Clauses that benefit the signer (max 3)
7. **KEY TERMS**: Legal jargon translated to plain English (max 5)
8. **QUESTIONS TO ASK**: What to clarify before signing (max 4)

**IMPORTANT RULES:**
- Use simple words a 15-year-old would understand
- Be specific about money, dates, and obligations
- Explain WHY something is good or bad, not just WHAT it is
- Focus on practical impact to the person's life"""

# --- Main Layout: Two Columns (Content | Chat) ---
main_col, chat_col = st.columns([2.2, 1], gap="medium")

with main_col:
    # --- Prompt Settings (Collapsed by Default) - Read Only ---
    with st.expander("🔍 View AI Prompts", expanded=False):
        st.markdown(f'''
        <div style="background: rgba(99, 102, 241, 0.05); border: 1px solid rgba(99, 102, 241, 0.15); border-radius: 0.5rem; padding: 1rem; margin-bottom: 1rem;">
            <div style="display: flex; align-items: center; gap: 0.5rem; color: #6366f1; font-weight: 600; font-size: 0.85rem; margin-bottom: 0.75rem;">
                <span class="material-symbols-outlined" style="font-size: 1rem;">psychology</span>
                System Instructions
            </div>
            <div style="background: rgba(0,0,0,0.2); border-radius: 0.375rem; padding: 0.75rem; max-height: 200px; overflow-y: auto; font-family: monospace; font-size: 0.75rem; color: #c7d2fe; line-height: 1.6; white-space: pre-wrap;">{st.session_state.system_prompt}</div>
        </div>
        <div style="background: rgba(99, 102, 241, 0.05); border: 1px solid rgba(99, 102, 241, 0.15); border-radius: 0.5rem; padding: 1rem;">
            <div style="display: flex; align-items: center; gap: 0.5rem; color: #6366f1; font-weight: 600; font-size: 0.85rem; margin-bottom: 0.75rem;">
                <span class="material-symbols-outlined" style="font-size: 1rem;">description</span>
                Analysis Prompt
            </div>
            <div style="background: rgba(0,0,0,0.2); border-radius: 0.375rem; padding: 0.75rem; max-height: 200px; overflow-y: auto; font-family: monospace; font-size: 0.75rem; color: #c7d2fe; line-height: 1.6; white-space: pre-wrap;">{st.session_state.analysis_prompt}</div>
        </div>
        ''', unsafe_allow_html=True)
    
    # --- Main Upload Section ---
    content_to_analyze = None
    input_type = None
    analyze_button = False

    # Collapse upload section after analysis is done
    with st.expander("📂 Upload Document", expanded='analysis_result' not in st.session_state):
        st.markdown("""
        <div class="section-title">
            <span class="material-symbols-outlined">upload_file</span>
            Upload Your Document
        </div>
        """, unsafe_allow_html=True)

        tab1, tab2, tab3 = st.tabs(["PDF", "Image", "Paste Text"])

        with tab1:
            pdf_file = st.file_uploader("Upload PDF", type=['pdf'], label_visibility="collapsed")
            if pdf_file:
                # Send PDF directly to Gemini (better than text extraction)
                pdf_bytes = pdf_file.read()
                pdf_file.seek(0)  # Reset for potential re-read
                content_to_analyze = {
                    "mime_type": "application/pdf",
                    "data": pdf_bytes
                }
                input_type = "pdf"
                st.success(f"PDF loaded ({len(pdf_bytes):,} bytes) - Sending directly to AI")

        with tab2:
            img_file = st.file_uploader("Upload Image", type=['png', 'jpg', 'jpeg', 'webp'], label_visibility="collapsed")
            if img_file:
                content_to_analyze = Image.open(img_file)
                input_type = "image"
                st.image(content_to_analyze, width="stretch")

        with tab3:
            text_input = st.text_area("Paste contract text", height=150, label_visibility="collapsed", placeholder="Paste your contract or legal document here...")
            if text_input and len(text_input.strip()) > 0:
                content_to_analyze = text_input.strip()
                input_type = "text"
                st.success(f"Text ready ({len(content_to_analyze):,} chars)")

        # --- Analyze Button ---
        analyze_col1, analyze_col2, analyze_col3 = st.columns([1, 2, 1])
        with analyze_col2:
            analyze_button = st.button("Analyze Document", type="primary", width="stretch")

    # --- Results Processing ---
    if analyze_button:
        if not content_to_analyze:
            st.error("Please upload a document or paste text first.")
        else:
            selected_lang = st.session_state.get('target_language', 'English')
            
            # Store original result in session state (pass target language for direct translation)
            result_text = analyze_contract(content_to_analyze, input_type, api_key, selected_lang)
            
            # Parse JSON once
            try:
                cleaned = result_text.strip()
                cleaned = re.sub(r'^```json\s*', '', cleaned)
                cleaned = re.sub(r'^```\s*', '', cleaned)
                cleaned = re.sub(r'\s*```$', '', cleaned)
                json_match = re.search(r'\{[\s\S]*\}', cleaned)
                if json_match:
                    cleaned = json_match.group()
                
                # Fix common JSON issues
                cleaned = re.sub(r',\s*}', '}', cleaned)
                cleaned = re.sub(r',\s*]', ']', cleaned)
                cleaned = re.sub(r'"\s*(?:and|AND)\s*"', ' and ', cleaned)
                cleaned = re.sub(r'}\s*{', '}, {', cleaned)
                
                data = json.loads(cleaned)
                st.session_state['analysis_result'] = data
                st.session_state['analysis_source'] = content_to_analyze
                st.session_state['analysis_input_type'] = input_type  # Store input type too
                st.session_state['last_analyzed_language'] = selected_lang  # Track what language was used
                st.session_state['show_chat'] = True
                
            except Exception as e:
                st.error(f"Failed to parse AI response: {str(e)}")
                with st.expander("View Debug Info"):
                    st.text("Raw Output:")
                    st.code(result_text)
                    st.text("Cleaned Output:")
                    st.code(cleaned)

    # --- Results Display ---
    if 'analysis_result' in st.session_state:
        st.markdown("---")
        
        # Translate existing result if language changed (much faster than re-analyzing)
        current_lang = st.session_state.get('target_language', 'English')
        last_analyzed_lang = st.session_state.get('last_analyzed_language', 'English')
        
        if current_lang != last_analyzed_lang:
            # Just translate the existing JSON - don't re-analyze the document!
            existing_result = st.session_state['analysis_result']
            
            # Show loading
            with st.spinner(f"Translating to {current_lang}..."):
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    
                    translate_prompt = f"""Translate ALL text values in this JSON to {current_lang}.
Keep the JSON structure and keys exactly the same (in English).
Only translate the VALUES to {current_lang}.

JSON to translate:
{json.dumps(existing_result, indent=2)}

Return ONLY the translated JSON. No explanation, no markdown."""
                    
                    response = model.generate_content(translate_prompt)
                    result_text = response.text
                    
                    # Parse the translated JSON
                    cleaned = result_text.strip()
                    cleaned = re.sub(r'^```json\s*', '', cleaned)
                    cleaned = re.sub(r'^```\s*', '', cleaned)
                    cleaned = re.sub(r'\s*```$', '', cleaned)
                    json_match = re.search(r'\{[\s\S]*\}', cleaned)
                    if json_match:
                        cleaned = json_match.group()
                    
                    data = json.loads(cleaned)
                    st.session_state['analysis_result'] = data
                    st.session_state['last_analyzed_language'] = current_lang
                    st.rerun()
                except Exception as e:
                    st.error(f"Translation failed: {str(e)}")
        
        # Display results (already in target language from Gemini)
        placeholders = display_results(st.session_state['analysis_result'])
        
        # Final Disclaimer
        st.markdown("""
        <div class="card card-red" style="margin-top: 1rem;">
            <div class="card-header">
                <span class="material-symbols-outlined">gavel</span>
                Important Reminder
            </div>
            <div class="card-content">
                <p>This analysis is for <strong>educational purposes only</strong> and is not legal advice. Before signing any legal document:</p>
                <ul>
                    <li>Consult with a qualified attorney</li>
                    <li>Ask questions if anything is unclear</li>
                    <li>Never feel pressured to sign immediately</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

# --- Right Side Chat Panel ---
with chat_col:
    # Header with clear button
    header_col1, header_col2 = st.columns([5, 1])
    with header_col1:
        st.markdown('''
        <div class="chat-panel-header" style="border-bottom: none; padding-bottom: 0; margin-bottom: 0;">
            <span class="material-symbols-outlined">smart_toy</span>
            Ask Questions
        </div>
        ''', unsafe_allow_html=True)
    with header_col2:
        # Small clear button - only show when there are messages
        if 'messages' in st.session_state and st.session_state.messages:
            if st.button("🗑️", key="clear_chat", help="Clear chat history"):
                st.session_state.messages = []
                if 'pending_question' in st.session_state:
                    del st.session_state['pending_question']
                st.rerun()
    
    # Divider line
    st.markdown('<hr style="margin: 0.5rem 0; border: none; border-top: 2px solid rgba(99, 102, 241, 0.3);">', unsafe_allow_html=True)
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Check if we have analysis results for context
    has_analysis = 'analysis_result' in st.session_state
    
    # If no analysis yet, show disabled state
    if not has_analysis:
        st.markdown('''
        <div class="chat-welcome" style="opacity: 0.6;">
            <span class="material-symbols-outlined">lock</span>
            <h4>Chat Disabled</h4>
            <p>Upload and analyze a document first to enable the chat feature.</p>
        </div>
        ''', unsafe_allow_html=True)
        st.markdown("<p style='font-size: 0.75rem; color: #64748b; text-align: center; margin-top: 1rem;'>⬆️ Start by uploading a document on the left</p>", unsafe_allow_html=True)
    
    # Chat messages container - only show if analysis is done
    elif not st.session_state.messages:
        # Welcome message when no chat history
        st.markdown('''
        <div class="chat-welcome">
            <span class="material-symbols-outlined">forum</span>
            <h4>Ask your questions here</h4>
            <p>Your document is ready! Ask me anything about it.</p>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('''
        <div class="doc-ready-badge">
            <div class="badge-header">
                <span class="material-symbols-outlined" style="font-size: 1rem;">check_circle</span>
                Document Ready
            </div>
            <p>Your document has been analyzed. Ask me anything!</p>
        </div>
        ''', unsafe_allow_html=True)
        
        # Suggestion chips - only show when analysis is ready
        st.markdown("<p style='font-size: 0.75rem; color: #94a3b8; margin-top: 1rem; margin-bottom: 0.5rem;'>Try asking:</p>", unsafe_allow_html=True)
        
        suggestion_cols = st.columns(1)
        with suggestion_cols[0]:
            suggestions = [
                "What are the main risks?",
                "Explain the termination clause",
                "What happens if I break this contract?",
                "Is this a fair agreement?"
            ]
            for suggestion in suggestions:
                if st.button(f"💬 {suggestion}", key=f"sug_{suggestion[:10]}", width="stretch"):
                    # Add user message
                    st.session_state.messages.append({"role": "user", "content": suggestion})
                    # Set flag to generate response
                    st.session_state['pending_question'] = suggestion
                    st.rerun()
    else:
        # Display chat messages
        chat_container = st.container()
        with chat_container:
            st.markdown('<div class="chat-messages-container">', unsafe_allow_html=True)
            for message in st.session_state.messages:
                if message["role"] == "user":
                    st.markdown(f'''
                    <div class="chat-bubble user-bubble">{message['content']}</div>
                    ''', unsafe_allow_html=True)
                else:
                    st.markdown(f'''
                    <div class="chat-bubble ai-bubble">
                        <strong>LegalLens</strong><br>{message['content']}
                    </div>
                    ''', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Handle pending question from suggestion buttons OR chat input
    pending_q = st.session_state.get('pending_question', None)
    
    # Chat input at bottom - only show when analysis is done
    if has_analysis:
        st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)
        
        prompt = st.chat_input("Type your question...", key="chat_input")
        
        # Use pending question if exists, otherwise use typed prompt
        question_to_answer = pending_q if pending_q else prompt
        
        if question_to_answer:
            # If it's from chat input, add the message first
            if prompt and not pending_q:
                st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Clear pending question
            if 'pending_question' in st.session_state:
                del st.session_state['pending_question']
            
            # Show typing indicator
            typing_placeholder = st.empty()
            typing_placeholder.markdown('''
            <div class="typing-indicator">
                <span>LegalLens is thinking</span>
                <div class="typing-dots">
                    <div></div>
                    <div></div>
                    <div></div>
                </div>
            </div>
            ''', unsafe_allow_html=True)
            
            try:
                context_data = st.session_state['analysis_result']
                full_context = f"Document Analysis: {json.dumps(context_data)}"
                
                chat_prompt = f"""You are LegalLens, a helpful legal document assistant.

{st.session_state.get('system_prompt', '')}

Document analysis context: {full_context}

User question: {question_to_answer}

Provide a helpful, concise answer. Use simple language. If the question is about something not in the document, say so clearly."""
                
                genai.configure(api_key=api_key)
                chat_model = genai.GenerativeModel('gemini-2.5-flash')
                response = chat_model.generate_content(chat_prompt)
                
                typing_placeholder.empty()
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                st.rerun()
            except Exception as e:
                typing_placeholder.empty()
                st.error(f"Error: {str(e)}")

# --- Footer ---
st.markdown("""
<div class="footer">
    <div style="display: flex; justify-content: center; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
        <span class="material-symbols-outlined" style="font-size: 1.2rem;">policy</span>
        <strong>LegalLens</strong>
    </div>
    <div style="font-size: 0.75rem; opacity: 0.8;">
        AI Advisory Tool Only — Always Seek Professional Legal Counsel
    </div>
</div>
""", unsafe_allow_html=True)
