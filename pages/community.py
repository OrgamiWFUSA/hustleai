import streamlit as st
from utils import get_bottom_nav_html, authenticate_user

st.set_page_config(page_title="Community - HustleAI", layout="wide", initial_sidebar_state="collapsed")

# Back button fix
st.markdown('<style> section[data-testid="stSidebar"] { display: none !important; } </style>', unsafe_allow_html=True)
st.experimental_set_query_params()

user = authenticate_user()
if not user:
    st.warning("Please sign in to join the community.")
    st.stop()

st.title("HustleAI Community Forum")

# Expanded: Simple post form and display (placeholder; expand with backend)
if 'posts' not in st.session_state:
    st.session_state.posts = []

post = st.text_area("Share your hustle idea or question")
if st.button("Post"):
    if post:
        st.session_state.posts.append({"user": user, "content": post})
        st.success("Posted!")

st.subheader("Recent Posts")
for p in st.session_state.posts:
    st.markdown(f"**{p['user']}:** {p['content']}")

st.markdown(get_bottom_nav_html("community"), unsafe_allow_html=True)