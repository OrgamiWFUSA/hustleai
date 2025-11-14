import streamlit as st
import requests
from pypdf2 import PdfReader

def get_bottom_nav_html(current_page=""):
    """
    Returns the HTML for the turquoise bottom navigation bar with active state.
    Expanded for better UX: Highlights the current page button.
    """
    buttons = {
        "Home": "/",
        "Checklist": "/checklist",
        "Community": "/community",
        "Account": "/account",
        "Settings": "/settings"
    }
    button_html = ""
    for label, url in buttons.items():
        active_class = ' class="active"' if current_page.lower() in url.lower() else ""
        button_html += f'<button{active_class} onclick="window.location.href=\'{url}\'">{label}</button>'
    
    return f"""
    <style>
        /* Bottom navigation bar styling - Meta-inspired clean look */
        .bottom-nav {{
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background-color: #40E0D0;  /* Turquoise */
            display: flex;
            justify-content: space-around;
            align-items: center;
            padding: 10px 0;
            box-shadow: 0 -2px 5px rgba(0,0,0,0.1);
            z-index: 1000;
        }}
        .bottom-nav button {{
            background: none;
            border: none;
            font-size: 16px;
            cursor: pointer;
            color: white;
            padding: 5px 10px;
            transition: color 0.3s;
        }}
        .bottom-nav button:hover {{
            color: #333;
        }}
        .bottom-nav button.active {{
            font-weight: bold;
            color: #333;
        }}
    </style>
    <div class="bottom-nav">
        {button_html}
    </div>
    """

def authenticate_user():
    """
    Expanded placeholder for user auth logic (session-based).
    Can integrate with Firebase or SQL later.
    """
    if 'user' not in st.session_state:
        st.session_state.user = None
    return st.session_state.user

def parse_resume_with_grok(resume_text, api_key):
    """
    Use Grok API for resume parsing (OpenAI-compatible format).
    Expanded with structured JSON output and error handling.
    """
    url = "https://api.x.ai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": "grok-beta",  # Use latest available; check docs
        "messages": [
            {"role": "system", "content": "You are a resume parser. Extract and return as JSON: name, email, phone, skills (list), experience (list of dicts with job_title, company, dates, bullets), education (list of dicts with degree, school, dates)."},
            {"role": "user", "content": f"Parse this resume text: {resume_text}"}
        ],
        "temperature": 0.5,
        "max_tokens": 2048
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        raise Exception(f"API error: {str(e)}")

def generate_hustle_ideas(location="", num_ideas=5, api_key=""):
    """
    New: AI-powered hustle idea generator using Grok API.
    Generates tailored ideas based on optional location.
    Returns list of formatted idea strings.
    """
    prompt = f"Generate {num_ideas} unique hustle/business ideas. Format each as: 'Idea #X: **Bold Header** - Bullet 1 - Bullet 2 - Bullet 3 - (up to 5 bullets)'. "
    if location:
        prompt += f"Tailor to {location} (e.g., local trends, needs)."
    else:
        prompt += "Make them general but actionable."
    
    url = "https://api.x.ai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": "grok-beta",
        "messages": [
            {"role": "system", "content": "You are a creative hustle idea generator for entrepreneurs."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 2048
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        raw_ideas = response.json()["choices"][0]["message"]["content"]
        # Split into list of ideas
        ideas = [idea.strip() for idea in raw_ideas.split("Idea #") if idea.strip()]
        ideas = [f"Idea #{i+1}: {idea}" for i, idea in enumerate(ideas)]
        return ideas
    except requests.exceptions.RequestException as e:
        raise Exception(f"Idea generation error: {str(e)}")