import json
import os
import streamlit as st

# Folders (from original code)
UPLOAD_DIR = "uploads"
CHECKLIST_DIR = "checklists"

def load_json(path, default):
    """Load JSON from file or return default."""
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def save_json(path, data):
    """Save data to JSON file."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def get_ip():
    """Get user's IP (for guest tracking)."""
    try:
        return st.context.headers.get("X-Forwarded-For", "unknown").split(',')[0].strip()
    except:
        return "unknown"

def get_bottom_nav_html():
    """Return HTML for bottom navigation."""
    return """
    <div class="bottom-nav">
        <a href="?page=Home" target="_self">Home</a>
        <a href="?page=Checklist" target="_self">Checklist</a>
        <a href="?page=Community" target="_self">Community</a>
        <a href="?page=Account" target="_self">Account</a>
        <a href="?page=Settings" target="_self">Settings</a>
    </div>
    """

def authenticate_user():
    """Handle user authentication check."""
    if 'user_email' not in st.session_state:
        st.warning("Please sign in to access this page.")
        st.experimental_set_query_params(page="Account")
        st.stop()
    # Additional auth logic can go here if needed (e.g., token validation)