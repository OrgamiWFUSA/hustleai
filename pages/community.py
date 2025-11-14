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
st.markdown("<h1 class='title'>Community Forum</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Share Your Wins!</p>", unsafe_allow_html=True)

if 'username' not in st.session_state:
    st.warning("Sign in to post.")
else:
    st.subheader("New Post")
    post_title = st.text_input("Title")
    post_body = st.text_area("Content")
    if st.button("Post"):
        if post_title and post_body:
            posts.append({
                "title": post_title,
                "content": post_body,
                "username": st.session_state.username,
                "replies": []
            })
            save_json("posts.json", posts)
            st.success("Posted!")
            st.rerun()
st.subheader("Recent Posts")
for i, post in enumerate(posts[::-1]):
    with st.expander(f"**{post['title']}** by {post['username']}"):
        st.write(post["content"])
        reply_text = st.text_area("Reply", key=f"r_post_{i}")
        if st.button("Reply", key=f"rb_post_{i}"):
            if reply_text:
                post["replies"].append({
                    "username": st.session_state.username,
                    "content": reply_text,
                    "replies": []
                })
                save_json("posts.json", posts)
                st.success("Replied!")
                st.rerun()
        def render(replies, depth=1, pkey=""):
            for j, r in enumerate(replies):
                indent = " " * depth
                with st.expander(f"{indent}↳ **{r['username']}**"):
                    st.write(r["content"])
                    sub = st.text_area("Reply", key=f"r_{pkey}_{i}_{j}")
                    if st.button("Reply", key=f"rb_{pkey}_{i}_{j}"):
                        if sub:
                            r["replies"].append({
                                "username": st.session_state.username,
                                "content": sub,
                                "replies": []
                            })
                            save_json("posts.json", posts)
                            st.success("Replied!")
                            st.rerun()
                        render(r["replies"], depth + 1, f"{pkey}_{i}_{j}")
        render(post["replies"])

# Bottom Navigation
st.markdown(bottom_nav_html, unsafe_allow_html=True)