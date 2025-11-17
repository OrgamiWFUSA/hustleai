import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import streamlit as st
from utils import bottom_nav, load_json, save_json, generate_checklist

st.set_page_config(page_title="Checklist - HustleAI", layout="centered", initial_sidebar_state="expanded")
bottom_nav()

if 'user_email' not in st.session_state:
    st.warning("Sign in to view your checklists.")
    st.stop()

st.title("My Checklists")
email = st.session_state.user_email
path = os.path.join("checklists", f"{email}.json")
data = load_json(path, [])
for idx, entry in enumerate(data):
    with st.expander(f"Liked Idea {idx+1}: {entry['idea'].splitlines()[0]}"):
        st.subheader("Your Liked Hustle")
        st.write(entry["idea"])
        st.subheader("Checklist")
        checklist = entry.get("checklist", generate_checklist(entry["idea"]))
        for i, item in enumerate(checklist):
            c1, c2 = st.columns([3,1])
            with c1: st.write(item["goal"])
            with c2:
                try:
                    due_value = datetime.strptime(item["due"], '%Y-%m-%d')
                except ValueError:
                    due_value = datetime.now() + timedelta(days=7)
                new_date = st.date_input("Due", value=due_value, key=f"due_{idx}_{i}")
                checklist[i]["due"] = new_date.strftime('%Y-%m-%d')
if st.button("Save Changes"):
    save_json(path, data)
    st.success("Checklists updated!")
else:
    st.info("No checklists yet – generate ideas and swipe right on one.")