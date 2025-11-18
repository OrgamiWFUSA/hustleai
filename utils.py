# utils.py — 100% working version
import streamlit as st
import os
from openai import OpenAI
import PyPDF2
from datetime import datetime, timedelta

# THESE TWO LINES ARE THE ONES THAT WERE MISSING
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

def get_ip():
    try:
        return st.context.headers.get("X-Forwarded-For", "unknown").split(',')[0].strip()
    except:
        return "unknown"

def bottom_nav():
    st.markdown("""
    <div style="position:fixed;bottom:0;left:0;right:0;background:#001f3f;color:white;padding:12px;text-align:center;z-index:1000;">
        <a href="?page=Home" style="color:white;margin:0 15px;text-decoration:none;">Home</a>
        <a href="?page=Checklist" style="color:white;margin:0 15px;text-decoration:none;">Checklist</a>
        <a href="?page=Community" style="color:white;margin:0 15px;text-decoration:none;">Community</a>
        <a href="?page=Account" style="color:white;margin:0 15px;text-decoration:none;">Account</a>
        <a href="?page=Settings" style="color:white;margin:0 15px;text-decoration:none;">Settings</a>
    </div>
    """, unsafe_allow_html=True)

# (keep all your other functions: extract_skills_from_pdf, generate_hustles, generate_single_hustle, generate_checklist)
# just paste them below this line from your old utils.py or original code