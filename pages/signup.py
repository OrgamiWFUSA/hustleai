import streamlit as st
from utils import get_bottom_nav_html, load_json, save_json

st.title("Sign Up for HustleAI")
username = st.text_input("Username")
email = st.text_input("Email")
password = st.text_input("Password", type="password")
if st.button("Sign Up"):
    if email in load_json("users.json", {}):
        st.error("Email already registered.")
    elif username and email and password:
        users = load_json("users.json", {})
        users[email] = {
            "username": username,
            "password": password,
            "free_count": 0,
            "is_pro": False
        }
        save_json("users.json", users)
        st.session_state.user_email = email
        st.session_state.username = username
        st.session_state.free_count = 0
        st.session_state.is_pro = False
        st.success("Signed up! Redirecting to home...")
        st.switch_page("app.py")  # Or '/'
    else:
        st.warning("Fill in all fields.")

st.markdown("Already have an account? [Sign In here](/account)")

# Render bottom nav
st.markdown(get_bottom_nav_html(), unsafe_allow_html=True)