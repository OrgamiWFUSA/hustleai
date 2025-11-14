# hustleai.py  ←  This file stays super simple
import streamlit as st

st.set_page_config(page_title="HustleAI", page_icon="rocket", layout="centered")

st.markdown("""
<style>
    .bottom-nav {
        position: fixed;
        bottom: 0; left: 0; right: 0;
        background-color: #001f3f;
        padding: 12px;
        display: flex;
        justify-content: space-around;
        z-index: 1000;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.3);
    }
    .bottom-nav a {
        color: white;
        text-decoration: none;
        font-weight: 600;
        font-size: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Optional: show logo on the main page only
try:
    st.image("logo.png", width=180)
except:
    pass

st.title("HustleAI")
st.caption("Turn your skills into side income — anywhere.")

# Bottom nav that appears on EVERY page
st.markdown(f"""
<div class="bottom-nav">
    <a href="/" target="_self">Home</a>
    <a href="/Checklist" target="_self">Checklist</a>
    <a href="/Community" target="_self">Community</a>
    <a href="/Account" target="_self">Account</a>
    <a href="/Settings" target="_self">Settings</a>
</div>
""", unsafe_allow_html=True)