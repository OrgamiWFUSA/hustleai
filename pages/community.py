import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import streamlit as st
from utils import bottom_nav, load_json, save_json

st.set_page_config(page_title="Community - HustleAI", layout="centered", initial_sidebar_state="expanded")
bottom_nav()

posts = load_json("posts.json", [])

st.title("Community Forum: Share Your Wins!")
if 'user_email' not in st.session_state:
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
        if 'user_email' in st.session_state:
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
                    if 'user_email' in st.session_state:
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