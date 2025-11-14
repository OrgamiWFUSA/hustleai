import streamlit as st
from utils import get_bottom_nav_html, generate_hustle_ideas

st.set_page_config(page_title="HustleAI Home", layout="wide", initial_sidebar_state="collapsed")

# PWA meta tags for app-like feel on phone
st.markdown("""
    <link rel="manifest" href="/manifest.json">
    <meta name="theme-color" content="#40E0D0">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black">
    <meta name="apple-mobile-web-app-title" content="HustleAI">
""", unsafe_allow_html=True)

# Back button fix
st.markdown('<style> section[data-testid="stSidebar"] { display: none !important; } </style>', unsafe_allow_html=True)
st.experimental_set_query_params()

st.title("Welcome to HustleAI")
st.write("Your AI-powered companion for hustle ideas, resume optimization, and career growth.")

# New: Idea Generator Section
st.subheader("Generate Hustle Ideas")
location = st.text_input("Optional: Enter a location to tailor ideas (e.g., 'San Francisco')")
num_ideas = st.slider("Number of ideas", 1, 10, 5)
api_key = "your_xai_api_key_here"  # Same as resume parsing

if st.button("Generate Ideas"):
    try:
        ideas = generate_hustle_ideas(location, num_ideas, api_key)
        st.session_state.ideas = ideas
        st.session_state.current_idea_index = 0
        st.success(f"Generated {len(ideas)} ideas!")
    except Exception as e:
        st.error(str(e))

# Expanded: Tinder-style swipe for ideas (fixes slow/double-click on phone)
if 'ideas' in st.session_state and st.session_state.ideas:
    index = st.session_state.current_idea_index
    st.markdown(st.session_state.ideas[index])
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("👎 Dislike (Previous)"):
            st.session_state.current_idea_index = max(0, index - 1)
            st.experimental_rerun()
    with col3:
        if st.button("👍 Like (Next)"):
            st.session_state.current_idea_index = min(len(st.session_state.ideas) - 1, index + 1)
            st.experimental_rerun()

# Render bottom nav with active
st.markdown(get_bottom_nav_html("home"), unsafe_allow_html=True)