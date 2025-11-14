# pages/account.py
import streamlit as st
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils import *

st.title("Account")

if 'user_email' in st.session_state:
    st.write(f"Logged in as {st.session_state.username}")
    if st.button("Log Out"):
        st.experimental_set_query_params(logout="true")
        st.rerun()

    # Upgrade section
    st.subheader("Upgrade to Pro")
    st.write("Freemium: 3 free ideas/month, $4.99 for unlimited.")
    st.write("Affiliates: Shopify, Canva links.")
    st.markdown("<script src='https://js.stripe.com/v3/'></script>", unsafe_allow_html=True)
    if st.button("Upgrade to Pro ($4.99/month)"):
        pass  # Add Stripe later
else:
    # Login
    st.subheader("Login")
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")
    if st.button("Sign In"):
        if email in users and users[email]["password"] == password:
            st.session_state.user_email = email
            st.session_state.username = users[email]["username"]
            st.session_state.free_count = users[email].get("free_count", 0)
            st.session_state.is_pro = users[email].get("is_pro", False)
            st.success(f"Signed in as {st.session_state.username}!")
            st.rerun()
        else:
            st.error("Invalid email or password")

    # Signup
    st.subheader("Sign Up")
    username = st.text_input("Username", key="signup_username")
    signup_email = st.text_input("Email", key="signup_email")
    signup_password = st.text_input("Password", type="password", key="signup_password")
    if st.button("Sign Up"):
        if signup_email not in users:
            users[signup_email] = {"username": username, "password": signup_password, "free_count": 0, "is_pro": False}
            save_json("users.json", users)
            st.session_state.user_email = signup_email
            st.session_state.username = username
            st.success("Signed up successfully!")
            st.rerun()
        else:
            st.error("Email already exists")

# Bottom navigation
st.markdown("""
<div style="position:fixed;bottom:0;left:0;right:0;background:#001f3f;padding:12px;display:flex;justify-content:space-around;z-index:1000;box-shadow:0 -2px 10px rgba(0,0,0,0.3);">
    <a href="/Home" style="color:white;text-decoration:none;font-weight:600;">Home</a>
    <a href="/Checklist" style="color:white;text-decoration:none;font-weight:600;">Checklist</a>
    <a href="/Community" style="color:white;text-decoration:none;font-weight:600;">Community</a>
    <a href="/Account" style="color:white;text-decoration:none;font-weight:600;">Account</a>
    <a href="/Settings" style="color:white;text-decoration:none;font-weight:600;">Settings</a>
</div>
""", unsafe_allow_html=True)