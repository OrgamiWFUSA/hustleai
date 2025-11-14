import streamlit as st
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils import *

st.title("Settings")

if 'user_email' in st.session_state:
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
else:
    st.warning("Sign in to access settings")

# Bottom navigation (added for you)
st.markdown("""
<style>
    .bottom-nav {position:fixed;bottom:0;left:0;right:0;background:#001f3f;padding:12px;display:flex;justify-content:space-around;z-index:1000;box-shadow:0 -4px 10px rgba(0,0,0,0.3);}
    .bottom-nav a {color:white;text-decoration:none;font-weight:600;}
</style>
<div class="bottom-nav">
    <a href="/" target="_self">Home</a>
    <a href="/Checklist" target="_self">Checklist</a>
    <a href="/Community" target="_self">Community</a>
    <a href="/Account" target="_self">Account</a>
    <a href="/Settings" target="_self">Settings</a>
</div>
""", unsafe_allow_html=True)