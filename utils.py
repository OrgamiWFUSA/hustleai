import streamlit as st
import os
import json
from datetime import datetime, timedelta
from openai import OpenAI
import PyPDF2

# Constants
UPLOAD_DIR = "uploads"
CHECKLIST_DIR = "checklists"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CHECKLIST_DIR, exist_ok=True)

GUESTS_FILE = "guests.json"

def load_json(path, default):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def get_ip():
    try:
        return st.context.headers.get("X-Forwarded-For", "unknown").split(',')[0].strip()
    except:
        return "unknown"

def extract_skills_from_pdf(uploaded_file):
    reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    
    text_lower = text.lower()
    
    common_skills = [
        "active listening", "communication", "computer skills", "customer service",
        "interpersonal skills", "leadership", "management", "problem-solving",
        "time management", "transferable skills", "verbal communication",
        "nonverbal communication", "written communication", "empathy",
        "emotional intelligence", "collaboration", "teamwork", "presentation skills",
        "negotiation", "conflict resolution", "adaptability", "creativity",
        "critical thinking", "organization", "attention to detail", "project management",
        "data analysis", "microsoft office", "excel", "powerpoint", "word",
        "google workspace", "programming", "python", "java", "sql", "javascript",
        "html", "css", "machine learning", "ai", "data science", "web development",
        "graphic design", "adobe creative suite", "photoshop", "illustrator",
        "sales", "marketing", "seo", "content creation", "social media management",
        "public speaking", "research", "analytical skills", "budgeting",
        "financial analysis", "accounting", "crm software", "salesforce",
        "networking", "multitasking", "initiative", "reliability", "work ethic"
    ]
    
    extracted_skills = [skill for skill in common_skills if skill.lower() in text_lower]
    extracted_skills = sorted(set(extracted_skills))
    
    return ', '.join(extracted_skills)

def generate_hustles(skills, location=""):
    location_prompt = f"in or near {location}" if location else "anywhere in the world"
    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"Generate 3 side hustle ideas for someone skilled in {skills}, {location_prompt}. "
                                                  "For each idea, provide the full complete response in this exact format (do not output partial responses, and no 'Idea #1' prefix):\n"
                                                  "**Subject**\n"
                                                  "First Month Overhead: $X (under $100)\n"
                                                  "First Month Income Potential: $Y-$Z\n"
                                                  "· Bullet point 1 with more detail of the idea\n"
                                                  "· Bullet point 2 with more detail of the idea\n"
                                                  "· Bullet point 3 with more detail of the idea\n"
                                                  "· Bullet point 4 with more detail of the idea\n"
                                                  "3-step launch plan:\n"
                                                  "1. Step 1\n"
                                                  "2. Step 2\n"
                                                  "3. Step 3\n\n"
                                                  "Example:\n"
                                                  "**Freelance Graphic Design Services**\n"
                                                  "First Month Overhead: $50 (under $100)\n"
                                                  "First Month Income Potential: $300-$800\n"
                                                  "· Leverage your graphic design skills to create logos, banners, and social media graphics for small businesses.\n"
                                                  "· Target local startups or online entrepreneurs who need affordable design work.\n"
                                                  "· Use free tools like Canva initially, upgrading as needed.\n"
                                                  "· Offer packages starting at low rates to build a portfolio quickly.\n"
                                                  "3-step launch plan:\n"
                                                  "1. Build a simple portfolio on a free site like Behance.\n"
                                                  "2. Post services on freelance platforms like Upwork or Fiverr.\n"
                                                  "3. Network on social media and reach out to potential clients."}]
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"OpenAI error: {e}")
        return "Error generating ideas."

def generate_single_hustle(skills, location=""):
    location_prompt = f"in or near {location}" if location else "anywhere"
    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"Generate 1 new side hustle idea for someone skilled in {skills}, {location_prompt}. "
                                                  "Provide the full complete response in this exact format (do not output partial responses, and no 'Idea #1' prefix):\n"
                                                  "**Subject**\n"
                                                  "First Month Overhead: $X (under $100)\n"
                                                  "First Month Income Potential: $Y-$Z\n"
                                                  "· Bullet point 1 with more detail of the idea\n"
                                                  "· Bullet point 2 with more detail of the idea\n"
                                                  "· Bullet point 3 with more detail of the idea\n"
                                                  "· Bullet point 4 with more detail of the idea\n"
                                                  "3-step launch plan:\n"
                                                  "1. Step 1\n"
                                                  "2. Step 2\n"
                                                  "3. Step 3\n"
                                                  "Example:\n"
                                                  "**Freelance Graphic Design Services**\n"
                                                  "First Month Overhead: $50 (under $100)\n"
                                                  "First Month Income Potential: $300-$800\n"
                                                  "· Leverage your graphic design skills to create logos, banners, and social media graphics for small businesses.\n"
                                                  "· Target local startups or online entrepreneurs who need affordable design work.\n"
                                                  "· Use free tools like Canva initially, upgrading as needed.\n"
                                                  "· Offer packages starting at low rates to build a portfolio quickly.\n"
                                                  "3-step launch plan:\n"
                                                  "1. Build a simple portfolio on a free site like Behance.\n"
                                                  "2. Post services on freelance platforms like Upwork or Fiverr.\n"
                                                  "3. Network on social media and reach out to potential clients."}]
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"OpenAI error: {e}")
        return "Error."

def generate_checklist(idea):
    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"Break down this side hustle idea into a checklist of 5-10 goals with specific due dates (start from today, spread over 1 month). Format exactly as a numbered list like '1. Goal - YYYY-MM-DD' where due dates are in YYYY-MM-DD format."}]
        )
        txt = response.choices[0].message.content
        lines = txt.split('\n')
        goals = []
        for line in lines:
            if line.strip():
                parts = line.split(' - ')
                if len(parts) == 2:
                    goal = parts[0].strip()
                    due_str = parts[1].strip()
                    try:
                        # Validate and parse the date
                        due_date = datetime.strptime(due_str, '%Y-%m-%d')
                        goals.append({"goal": goal, "due": due_date.strftime('%Y-%m-%d')})
                    except ValueError:
                        # If invalid, use default
                        goals.append({"goal": goal, "due": (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')})
                else:
                    goals.append({"goal": line.strip(), "due": (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')})
        return goals
    except Exception as e:
        st.error(f"OpenAI error: {e}")
        return []

# GUEST TRACKING
guests = load_json(GUESTS_FILE, {})

# Bottom Nav CSS (shared in utils.py for all pages to import)
bottom_nav_css = """
<style>
    .bottom-nav {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background-color: #001f3f;
        padding: 10px;
        color: white;
        display: flex;
        justify-content: space-around;
        z-index: 1000;
        box-shadow: 0 -2px 5px rgba(0,0,0,0.2);
    }
    .bottom-nav a {
        color: white;
        text-decoration: none;
        font-size: 1rem;
        padding: 5px 10px;
    }
</style>
"""
bottom_nav_html = """
<div class="bottom-nav">
    <a href="/Home" target="_self">Home</a>
    <a href="/Checklist" target="_self">Checklist</a>
    <a href="/Community" target="_self">Community</a>
    <a href="/Account" target="_self">Account</a>
    <a href="/Settings" target="_self">Settings</a>
</div>
"""