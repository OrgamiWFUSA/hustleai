import streamlit as st
from utils import get_bottom_nav_html, authenticate_user

st.set_page_config(page_title="Settings - HustleAI", layout="wide", initial_sidebar_state="collapsed")

# Back button fix
st.markdown('<style> section[data-testid="stSidebar"] { display: none !important; } </style>', unsafe_allow_html=True)
st.experimental_set_query_params()

user = authenticate_user()
if not user:
    st.warning("Please sign in to access settings.")
    st.stop()

st.title("App Settings")

# Expanded: Sample toggles
st.checkbox("Enable dark mode (coming soon)")
st.checkbox("Receive email notifications")
st.selectbox("Idea generation preference", ["General", "Tech-focused", "Local business"])
if st.button("Save Changes"):
    st.success("Settings saved!")

st.markdown(get_bottom_nav_html("settings"), unsafe_allow_html=True)