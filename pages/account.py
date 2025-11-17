import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import streamlit as st
from utils import bottom_nav, load_json, save_json

st.set_page_config(page_title="Account - HustleAI", layout="centered", initial_sidebar_state="expanded")
bottom_nav()

users = load_json("users.json", {})

st.title("Account")
if 'user_email' in st.session_state:
    st.write(f"Logged in as {st.session_state.username}")
    if st.button("Log Out"):
        st.experimental_set_query_params(logout="true")
        st.rerun()
    st.subheader("Upgrade to Pro")
    st.write("Freemium: 3 free ideas/month, $4.99 for unlimited.")
    st.write("Affiliates: Shopify, Canva links.")
    st.markdown("<script src='https://js.stripe.com/v3/'></script>", unsafe_allow_html=True)
    if st.button("Upgrade to Pro ($4.99/month)"):
        pass  # Stripe code here
else:
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
            st.experimental_set_query_params(page="Home")
            st.rerun()
        else:
            st.error("Invalid email or password.")
    st.write("New user?")
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
            st.experimental_set_query_params(page="Home")
            st.rerun()
        else:
            st.error("Email already exists.")