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
st.markdown("<h1 class='title'>My Checklists</h1>", unsafe_allow_html=True)

if 'user_email' in st.session_state:
    email = st.session_state.user_email
    path = os.path.join(CHECKLIST_DIR, f"{email}.json")
    if os.path.exists(path):
        data = load_json(path, [])
        for idx, entry in enumerate(data):
            with st.expander(f"Liked Idea {idx+1}: {entry['idea'].splitlines()[0]}"):
                st.subheader("Your Liked Hustle")
                st.write(entry["idea"])
                st.subheader("Checklist")
                checklist = entry.get("checklist", [])
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
else:
    st.warning("Sign in to view your checklists.")

# Bottom Navigation
st.markdown(bottom_nav_html, unsafe_allow_html=True)