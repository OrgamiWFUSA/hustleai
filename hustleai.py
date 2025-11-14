# hustleai.py  ← This IS your Home page (main page)
import streamlit as st
from openai import OpenAI
import PyPDF2
import os
import json
from datetime import datetime, timedelta

st.set_page_config(page_title="HustleAI", page_icon="rocket", layout="centered")

# === FOLDERS & JSON HELPERS ===
UPLOAD_DIR = "uploads"
CHECKLIST_DIR = "checklists"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CHECKLIST_DIR, exist_ok=True)

def load_json(path, default):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

users = load_json("users.json", {})
posts = load_json("posts.json", {})
guests = load_json("guests.json", {})

def get_ip():
    try:
        return st.context.headers.get("X-Forwarded-For", "unknown").split(',')[0].strip()
    except:
        return "unknown"

# === EXTRACT SKILLS FROM PDF ===
def extract_skills_from_pdf(uploaded_file):
    reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    text_lower = text.lower()
    common_skills = [
        "communication", "python", "leadership", "excel", "javascript", "marketing", "sales",
        "photoshop", "teamwork", "sql", "project management", "public speaking", "data analysis",
        "graphic design", "customer service", "active listening", "problem-solving", "creativity"
    ]
    extracted = [s for s in common_skills if s in text_lower]
    return ', '.join(sorted(set(extracted)))

# === GENERATE HUSTLES ===
def generate_hustles(skills, location=""):
    location_prompt = f"in or near {location}" if location else "anywhere"
    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"Generate 3 side hustle ideas for skills: {skills}. {location_prompt}. "
                                                  "Format exactly:\n**Title**\nOverhead: $X\nIncome: $Y-$Z\n• bullet\n• bullet\n3-step plan:\n1. ...\n2. ...\n3. ..."}]
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error("AI error")
        return "Error"

def generate_single_hustle(skills, location=""):
    location_prompt = f"in or near {location}" if location else "anywhere"
    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"Generate 1 new side hustle idea for skills: {skills}. {location_prompt}. Same format as above."}]
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error("AI error")
        return "Error"

def generate_checklist(idea):
    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"Break down this idea into a 5-10 item checklist with due dates: {idea}"}]
        )
        return response.choices[0].message.content.split("\n")
    except:
        return []

# === CSS & LAYOUT ===
st.markdown("""
<style>
    .main {background: linear-gradient(135deg, #e0f7fa, #ffffff); padding: 2rem;}
    .idea-card {background:white; padding:2rem; border-radius:20px; box-shadow:0 10px 30px rgba(0,0,0,0.15); margin:2rem 0; border-left:6px solid #42a5f5;}
    .bottom-nav {position:fixed;bottom:0;left:0;right:0;background:#001f3f;padding:12px;display:flex;justify-content:space-around;z-index:1000;}
    .bottom-nav a {color:white;text-decoration:none;font-weight:600;}
</style>
""", unsafe_allow_html=True)

try:
    st.image("logo.png", width=180)
except:
    pass

st.title("HustleAI")
st.caption("Turn your skills into side income — anywhere.")

# === FULL ORIGINAL HOME PAGE LOGIC ===
if 'user_email' not in st.session_state:
    ip = get_ip()
    if guests.get(ip, 0) >= 3:
        st.warning("Free limit reached. Sign up to continue!")
        st.stop()

# Load saved skills
extracted_skills = ""
if 'user_email' in st.session_state:
    email = st.session_state.user_email
    path = os.path.join(UPLOAD_DIR, f"{email}_skills.txt")
    if os.path.exists(path):
        with open(path, "r") as f:
            extracted_skills = f.read()
        st.success("Skills loaded!")

# Resume upload + generate
uploaded_file = st.file_uploader("Upload resume (TXT/PDF)", type=['txt','pdf'])
additional_skills = st.text_input("Additional skills (optional):")
location = st.text_input("Your city (optional):", placeholder="e.g. Miami")

if uploaded_file:
    if 'user_email' not in st.session_state:
        st.error("Sign in to save resume.")
    else:
        email = st.session_state.user_email
        ext = uploaded_file.name.split('.')[-1]
        with open(os.path.join(UPLOAD_DIR, f"{email}_resume.{ext}"), "wb") as f:
            f.write(uploaded_file.getbuffer())
        extracted = extract_skills_from_pdf(uploaded_file) if ext == "pdf" else uploaded_file.read().decode()
        with open(os.path.join(UPLOAD_DIR, f"{email}_skills.txt"), "w") as f:
            f.write(extracted)
        st.success("Resume saved!")
        extracted_skills = extracted

final_skills = extracted_skills + (", " + additional_skills if additional_skills else "")

if st.button("Generate My Hustles") and final_skills:
    with st.spinner("Thinking..."):
        ideas = generate_hustles(final_skills, location)
    st.session_state.ideas_list = ideas.strip().split("\n\n")
    st.session_state.idea_index = 0
    st.success("Ready! Swipe →")

# Swipe cards
if 'ideas_list' in st.session_state and st.session_state.ideas_list:
    index = st.session_state.idea_index
    if index < len(st.session_state.ideas_list):
        idea = st.session_state.ideas_list[index]
        st.markdown(f"<div class='idea-card'><pre>{idea}</pre></div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1,2,1])
        with c1:
            if st.button("👎 Dislike"):
                new = generate_single_hustle(final_skills, location)
                st.session_state.ideas_list[index] = new
                st.session_state.idea_index += 1
                st.rerun()
        with c3:
            if st.button("❤️ Like"):
                if 'user_email' in st.session_state:
                    path = os.path.join(CHECKLIST_DIR, f"{st.session_state.user_email}.json")
                    data = load_json(path, [])
                    data.append({"idea": idea, "checklist": generate_checklist(idea)})
                    save_json(path, data)
                    st.success("Saved to Checklist!")
                st.session_state.idea_index += 1
                st.rerun()

# === BOTTOM NAV (correct URLs) ===
st.markdown("""
<div class="bottom-nav">
    <a href="/" target="_self">Home</a>
    <a href="/Checklist" target="_self">Checklist</a>
    <a href="/Community" target="_self">Community</a>
    <a href="/Account" target="_self">Account</a>
    <a href="/Settings" target="_self">Settings</a>
</div>
""", unsafe_allow_html=True)