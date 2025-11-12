import streamlit as st
import json
import os

# Correct path: save users.json in the main hustleai folder
USERS_FILE = "../users.json"  # This goes up one level from pages/ to hustleai/

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)

users = load_users()

st.title("Sign Up for HustleAI")
st.write("Create an account to save your ideas, join the community, and unlock pro features!")

email = st.text_input("Email")
password = st.text_input("Password", type="password")
if st.button("Create Account"):
    if email in users:
        st.error("Email already exists.")
    else:
        st.session_state.temp_email = email
        st.session_state.temp_password = password
        st.session_state.signed_up = True
        st.success("Account created! Choose a username.")

if st.session_state.get("signed_up"):
    username = st.text_input("Choose Username")
    if st.button("Set Username"):
        email = st.session_state.temp_email
        users[email] = {"password": st.session_state.temp_password, "username": username}
        save_users(users)  # This now creates users.json in the right place
        st.session_state.user_email = email
        st.session_state.username = username
        st.success(f"Welcome, {username}!")
        # Clean up temp data
        for key in ["temp_email", "temp_password", "signed_up"]:
            if key in st.session_state:
                del st.session_state[key]
        st.switch_page("hustleai.py")