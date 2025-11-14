import streamlit as st

st.set_page_config(page_title="HustleAI", page_icon="rocket", layout="centered")

# Custom CSS for Bottom Navigation
st.markdown("""
<style>
    .bottom-nav {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background-color: #001f3f;
        padding: 10px;
        color: white;
        display: flex;
        justify-content: space-around;
        z-index: 1000;
        box-shadow: 0 -2px 5px rgba(0,0,0,0.2);
    }
    .bottom-nav a {
        color: white;
        text-decoration: none;
        font-size: 1rem;
        padding: 5px 10px;
    }
</style>
""", unsafe_allow_html=True)

# Optional landing content
st.title("HustleAI")
st.caption("Turn your skills into side income — anywhere.")
try:
    st.image("logo.png", width=180)
except:
    pass

# Bottom Navigation (will appear on all pages)
st.markdown("""
<div class="bottom-nav">
    <a href="/Home" target="_self">Home</a>
    <a href="/Checklist" target="_self">Checklist</a>
    <a href="/Community" target="_self">Community</a>
    <a href="/Account" target="_self">Account</a>
    <a href="/Settings" target="_self">Settings</a>
</div>
""", unsafe_allow_html=True)