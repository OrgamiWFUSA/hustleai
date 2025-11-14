import streamlit as st
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils import *

st.markdown("""
<style>
    .main {background: linear-gradient(135deg, #e0f7fa, #ffffff); padding: 2rem; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);}
    .logo {display: block; margin: 0 auto 1rem auto; max-width: 180px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);}
    .title {font-size: 2.8rem; font-weight: 700; text-align: center; color: #1565c0; margin-bottom: 0.5rem; font-family: Arial, sans-serif;}
    .subtitle {text-align: center; color: #555; font-size: 1.1rem; margin-bottom: 2rem;}
    .stButton>button {background: linear-gradient(45deg, #42a5f5, #1976d2); color: white; border: none; padding: 0.8rem 2rem; border-radius: 30px; font-weight: 600; box-shadow: 0 4px 15px rgba(0,0,0,0.2);}
    .stButton>button:hover {transform: translateY(-3px); box-shadow: 0 8px 20px rgba(0,0,0,0.3);}
    .stTextInput>div>div>input {border-radius: 12px; border: 1px solid #90caf9; padding: 0.8rem;}
</style>
""", unsafe_allow_html=True)

# Logo
try:
    st.image("logo.png", use_column_width=False, width=180)
except:
    pass
st.markdown("<h1 class='title'>Account</h1>", unsafe_allow_html=True)

if 'user_email' in st.session_state:
    st.write(f"Logged in as {st.session_state.username}")
    if st.button("Log Out"):
        st.experimental_set_query_params(logout="true")
        st.rerun()
    # Monetization section
    st.subheader("Upgrade to Pro")
    st.write("Freemium: 3 free ideas/month, $4.99 for unlimited.")
    st.write("Affiliates: Shopify, Canva links.")
    st.markdown(f"<script src='https://js.stripe.com/v3/'></script>", unsafe_allow_html=True)
    if st.button("Upgrade to Pro ($4.99/month)"):
        pass # Add Stripe later
else:
    # Login Form
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
            st.rerun()  # Simplified to reload current page
        else:
            st.error("Invalid email or password.")
    st.write("New user?")
    # Signup Form
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
            st.session_state.free_count = 0
            st.session_state.is_pro = False
            st.success("Signed up successfully!")
            st.rerun()  # Simplified to reload current page
        else:
            st.error("Email already exists.")

# Bottom Navigation
st.markdown(bottom_nav_html, unsafe_allow_html=True)