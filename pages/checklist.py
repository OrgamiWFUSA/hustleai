# pages/checklist.py
import streamlit as st
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils import *

st.title("My Hustle Checklists")

if 'user_email' not in st.session_state:
    st.warning("Sign in to view your checklists")
    st.stop()

email = st.session_state.user_email
path = os.path.join(CHECKLIST_DIR, f"{email}.json")

if not os.path.exists(path):
    st.info("No checklists yet – go to **Home** and swipe right on an idea!")
    st.stop()

data = load_json(path, [])

for idx, entry in enumerate(data):
    idea = entry["idea"]
    with st.expander(f"**{idea.splitlines()[0]}**", expanded=True):
        st.write(idea)

        # Regenerate if missing or user clicks
        if "checklist" not in entry or st.button("Regenerate Plan", key=f"regen_{idx}"):
            with st.spinner("Creating your step-by-step launch plan..."):
                steps = generate_checklist(idea)
                entry["checklist"] = steps
                save_json(path, data)
            st.success("Plan generated!")

        checklist = entry.get("checklist", [])
        if not checklist:
            st.warning("No steps yet. Click 'Regenerate Plan'.")
        else:
            for i, step in enumerate(checklist):
                c1, c2 = st.columns([4, 1])
                with c1:
                    st.write(f"**{i+1}.** {step['goal']}")
                with c2:
                    try:
                        due = datetime.strptime(step["due"], "%Y-%m-%d")
                    except:
                        due = datetime.now() + timedelta(days=7)
                    new_due = st.date_input(
                        "Due", value=due, key=f"due_{idx}_{i}",
                        label_visibility="collapsed"
                    )
                    checklist[i]["due"] = new_due.strftime("%Y-%m-%d")

        if st.button("Save Changes", key=f"save_{idx}"):
            save_json(path, data)
            st.success("Checklist saved!")

# Bottom nav (same as before)
st.markdown("""
<style>
    .bottom-nav {position:fixed;bottom:0;left:0;right:0;background:#00D1B2;padding:14px;display:flex;justify-content:space-around;z-index:9999;box-shadow:0 -4px 20px rgba(0,0,0,0.3);font-weight:600;}
    .bottom-nav a {color:white;text-decoration:none;}
</style>
<div class="bottom-nav">
    <a href="/" target="_self">Home</a>
    <a href="/checklist" target="_self">Checklist</a>
    <a href="/community" target="_self">Community</a>
    <a href="/account" target="_self">Account</a>
    <a href="/settings" target="_self">Settings</a>
</div>
""", unsafe_allow_html=True)