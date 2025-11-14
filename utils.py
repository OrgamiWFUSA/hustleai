import streamlit as st
import requests
import json
from datetime import datetime, timedelta
from PyPDF2 import PdfReader
import os

# Folders (shared)
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

# Guest tracking (shared)
GUESTS_FILE = "guests.json"
def get_ip():
    try:
        return st.context.headers.get("X-Forwarded-For", "unknown").split(',')[0].strip()
    except:
        return "unknown"

# Bottom nav HTML (shared across pages)
def get_bottom_nav_html():
    return """
    <style>
        .bottom-nav {
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
        }
        .bottom-nav button {
            background: none;
            border: none;
            font-size: 16px;
            cursor: pointer;
            color: white;
            padding: 5px 10px;
            transition: color 0.3s;
        }
        .bottom-nav button:hover {
            color: #333;
        }
        .bottom-nav button.active {
            font-weight: bold;
            color: #333;
        }
    </style>
    <div class="bottom-nav">
        <button onclick="window.location.href='/'">Home</button>
        <button onclick="window.location.href='/checklist'">Checklist</button>
        <button onclick="window.location.href='/community'">Community</button>
        <button onclick="window.location.href='/account'">Account</button>
        <button onclick="window.location.href='/monetization'">Upgrade</button>
    </div>
    """

# AI functions (switched to xAI/Grok)
def generate_hustles(skills, api_key):
    try:
        url = "https://api.x.ai/v1/chat/completions"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
        data = {
            "model": "grok-beta",
            "messages": [{"role": "user", "content": f"Generate 3 side hustle ideas for someone skilled in {skills}. Each idea should include: 1. Startup cost (under $100) 2. First month earnings potential ($100-$1000) 3. 3-step launch plan with specific actions. Format as numbered list with bold headings."}],
            "temperature": 0.7,
            "max_tokens": 1024
        }
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        st.error(f"xAI error: {e}")
        return "Error generating ideas."

def generate_single_hustle(skills, api_key):
    try:
        url = "https://api.x.ai/v1/chat/completions"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
        data = {
            "model": "grok-beta",
            "messages": [{"role": "user", "content": f"Generate 1 side hustle idea for someone skilled in {skills}. Include: 1. Startup cost (under $100) 2. First month earnings potential ($100-$1000) 3. 3-step launch plan with specific actions. Format with bold headings."}],
            "temperature": 0.7,
            "max_tokens": 512
        }
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        st.error(f"xAI error: {e}")
        return "Error."

def generate_checklist(idea, api_key):
    try:
        url = "https://api.x.ai/v1/chat/completions"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
        data = {
            "model": "grok-beta",
            "messages": [{"role": "user", "content": f"Break down this side hustle idea '{idea}' into a checklist of 5-10 goals with specific due dates (start from today, spread over 1 month). Format as numbered list with 'Goal - Due Date'."}],
            "temperature": 0.5,
            "max_tokens": 1024
        }
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        txt = response.json()["choices"][0]["message"]["content"]
        lines = txt.split('\n')
        goals = []
        for line in lines:
            if line.strip():
                parts = line.split(' - ')
                goal = parts[0].strip()
                due = parts[1].strip() if len(parts) > 1 else (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
                goals.append({"goal": goal, "due": due})
        return goals
    except Exception as e:
        st.error(f"xAI error: {e}")
        return []

def extract_skills_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text.strip()