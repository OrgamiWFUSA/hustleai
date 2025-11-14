import streamlit as st
from ..utils import *  # Import shared functions

st.title("Account")
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
            st.experimental_set_query_params(page="Home")
            st.rerun()
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
            st.experimental_set_query_params(page="Home")
            st.rerun()
        else:
            st.error("Email already exists.")

# Bottom Navigation
st.markdown("""
<div class="bottom-nav">
    <a href="/Home" target="_self">Home</a>
    <a href="/Checklist" target="_self">Checklist</a>
    <a href="/Community" target="_self">Community</a>
    <a href="/Account" target="_self">Account</a>
    <a href="/Settings" target="_self">Settings</a>
</div>
""", unsafe_allow_html=True)