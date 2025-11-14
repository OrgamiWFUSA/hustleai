import streamlit as st
from ..utils import *  # Import shared functions

st.title("My Checklists")
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
st.markdown("""
<div class="bottom-nav">
    <a href="/Home" target="_self">Home</a>
    <a href="/Checklist" target="_self">Checklist</a>
    <a href="/Community" target="_self">Community</a>
    <a href="/Account" target="_self">Account</a>
    <a href="/Settings" target="_self">Settings</a>
</div>
""", unsafe_allow_html=True)