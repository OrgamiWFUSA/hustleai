# pages/checklist.py
import streamlit as st
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils import *

st.title("My Launch Checklists")

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
        st.markdown(f"<div style='background:white;padding:1.5rem;border-radius:12px;margin:1rem 0;box-shadow:0 4px 12px rgba(0,0,0,0.1);'>{idea}</div>", unsafe_allow_html=True)

        # === REGENERATE IF NEEDED ===
        if "checklist" not in entry or st.button("Regenerate 30-Day Plan", key=f"regen_{idx}"):
            with st.spinner("Building your day-by-day launch plan..."):
                plan = generate_checklist(idea)
                entry["checklist"] = plan
                save_json(path, data)
            st.success("30-day roadmap generated!")

        checklist = entry.get("checklist", [])
        if not checklist:
            st.warning("No plan yet. Click 'Regenerate 30-Day Plan'.")
            continue

        # === DISPLAY EACH HEADLINE GOAL ===
        for i, goal in enumerate(checklist):
            due = goal.get("due", "")
            try:
                due_date = datetime.strptime(due, "%Y-%m-%d")
            except:
                due_date = datetime.now() + timedelta(days=i*2 + 3)

            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**Goal {i+1}: {goal['goal']}**")
            with col2:
                new_due = st.date_input(
                    "Due", value=due_date, key=f"due_{idx}_{i}",
                    label_visibility="collapsed"
                )
                checklist[i]["due"] = new_due.strftime("%Y-%m-%d")

            # Sub-tasks
            for task in goal.get("sub_tasks", []):
                st.markdown(f"&nbsp;&nbsp;• {task}")

            st.markdown("---")

        if st.button("Save All Changes", key=f"save_{idx}"):
            save_json(path, data)
            st.success("All changes saved!")

# === TURQUOISE BOTTOM NAV ===
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