import streamlit as st
from utils import get_bottom_nav_html

st.set_page_config(page_title="Sign Up - HustleAI", layout="wide", initial_sidebar_state="collapsed")

# Back button fix
st.markdown('<style> section[data-testid="stSidebar"] { display: none !important; } </style>', unsafe_allow_html=True)
st.experimental_set_query_params()

st.title("Sign Up for HustleAI")
name = st.text_input("Full Name")
email = st.text_input("Email")
password = st.text_input("Password", type="password")
if st.button("Sign Up"):
    # Placeholder registration
    st.session_state.user = email
    st.success("Account created! Redirecting to account...")
    st.experimental_set_query_params(page="account")

st.markdown("Already have an account? [Sign In here](/account)")

# Render bottom nav (no active for signup, as it's separate)
st.markdown(get_bottom_nav_html(), unsafe_allow_html=True)