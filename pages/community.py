import streamlit as st
from ..utils import *  # Import shared functions

st.title("Community Forum: Share Your Wins!")
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
st.markdown("""
<div class="bottom-nav">
    <a href="/Home" target="_self">Home</a>
    <a href="/Checklist" target="_self">Checklist</a>
    <a href="/Community" target="_self">Community</a>
    <a href="/Account" target="_self">Account</a>
    <a href="/Settings" target="_self">Settings</a>
</div>
""", unsafe_allow_html=True)