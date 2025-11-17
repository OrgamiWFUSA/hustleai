import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import streamlit as st
from utils import bottom_nav, load_json, save_json

st.set_page_config(page_title="Settings - HustleAI", layout="centered", initial_sidebar_state="expanded")
bottom_nav()

if 'user_email' not in st.session_state:
    st.warning("Sign in to access settings.")
    st.stop()

users = load_json("users.json", {})

st.title("Settings")
email = st.session_state.user_email
st.subheader("Account Information")
st.write(f"Username: {st.session_state.username}")
st.write(f"Email: {email}")
st.write(f"Subscription: {'Pro' if st.session_state.is_pro else 'Free'}")

st.subheader("Change Password")
current_password = st.text_input("Current Password", type="password")
new_password = st.text_input("New Password", type="password")
confirm_password = st.text_input("Confirm New Password", type="password")
if st.button("Update Password"):
    if current_password == users[email]["password"]:
        if new_password == confirm_password and new_password:
            users[email]["password"] = new_password
            save_json("users.json", users)
            st.success("Password updated!")
        else:
            st.error("New passwords do not match or are empty.")
    else:
        st.error("Current password is incorrect.")