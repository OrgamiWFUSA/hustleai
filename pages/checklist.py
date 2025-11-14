import streamlit as st
from utils import get_bottom_nav_html, authenticate_user, parse_resume_with_grok
from pypdf2 import PdfReader

st.set_page_config(page_title="Checklist - HustleAI", layout="wide", initial_sidebar_state="collapsed")

# Back button fix
st.markdown('<style> section[data-testid="stSidebar"] { display: none !important; } </style>', unsafe_allow_html=True)
st.experimental_set_query_params()

user = authenticate_user()
if not user:
    st.warning("Please sign in to access the checklist.")
    st.stop()

st.title("Resume Checklist & AI Analysis")

uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])

if uploaded_file:
    st.subheader("AI-Powered Resume Analysis")
    try:
        # Extract text from PDF (handles multi-page)
        reader = PdfReader(uploaded_file)
        resume_text = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                resume_text += text + "\n"
        
        if not resume_text.strip():
            raise ValueError("No text extracted from PDF. Try a different file.")
        
        # Call Grok API for structured parsing
        api_key = "your_xai_api_key_here"  # Replace with your key from https://x.ai/api
        analysis_json = parse_resume_with_grok(resume_text, api_key)
        st.json(analysis_json)  # Display parsed JSON
        
        # Expanded: Auto-generate checklist based on analysis
        analysis = eval(analysis_json) if isinstance(analysis_json, str) else analysis_json  # Safe eval if string
        has_skills = bool(analysis.get("skills"))
        has_experience = bool(analysis.get("experience"))
        has_education = bool(analysis.get("education"))
        
        st.subheader("Auto-Generated Checklist")
        st.checkbox("Skills section present and relevant", value=has_skills)
        st.checkbox("Experience with quantifiable achievements", value=has_experience and any("bullets" in exp for exp in analysis.get("experience", [])))
        st.checkbox("Education details complete", value=has_education)
        st.checkbox("No obvious errors (e.g., missing contact info)", value=bool(analysis.get("email")) and bool(analysis.get("phone")))
    except Exception as e:
        st.error(f"Error processing resume: {str(e)}. Ensure PDF is text-based (not scanned).")

# Manual checklist (expanded with more items)
st.subheader("Manual Resume Checklist")
st.checkbox("Tailored to specific job description")
st.checkbox("Quantifiable achievements in experience")
st.checkbox("Keywords from job posting included")
st.checkbox("No typos or grammatical errors")
st.checkbox("Consistent formatting and fonts")

# Render bottom nav with active
st.markdown(get_bottom_nav_html("checklist"), unsafe_allow_html=True)