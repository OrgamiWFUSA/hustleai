import streamlit as st
from ..utils import *  # Import shared functions from utils.py

st.title("HustleAI Home")
# GUEST LIMIT
if 'user_email' not in st.session_state:
    ip = get_ip()
    if guests.get(ip, 0) >= 3:
        st.warning("Free limit reached (3 ideas). Sign up to continue!")
        st.stop()
else:
    if 'free_count' not in st.session_state:
        st.session_state.free_count = users[st.session_state.user_email].get("free_count", 0)
    if 'is_pro' not in st.session_state:
        st.session_state.is_pro = users[st.session_state.user_email].get("is_pro", False)

# Load saved skills
extracted_skills = ""
if 'user_email' in st.session_state:
    email = st.session_state.user_email
    skills_path = os.path.join(UPLOAD_DIR, f"{email}_skills.txt")
    if os.path.exists(skills_path):
        with open(skills_path, "r", encoding="utf-8") as f:
            extracted_skills = f.read()
        st.success("Skills loaded from your saved resume!")

if 'user_email' in st.session_state and st.session_state.free_count >= 3 and not st.session_state.is_pro:
    st.warning("Free limit reached (3 ideas/month). Upgrade for unlimited!")
    st.info("Pro: $4.99/month – unlimited ideas, priority AI, exclusive templates.")
else:
    uploaded_file = st.file_uploader("Upload resume (TXT/PDF)", type=['txt', 'pdf'])
    additional_skills = st.text_input("Additional skills (optional, e.g., video editing, Spanish, cooking):")
    location = st.text_input("Your city or country (optional, for local ideas):", placeholder="e.g., Miami, USA or Remote")
    if uploaded_file:
        if 'user_email' not in st.session_state:
            st.error("Sign in to save resume.")
        else:
            email = st.session_state.user_email
            ext = uploaded_file.name.split('.')[-1]
            file_path = os.path.join(UPLOAD_DIR, f"{email}_resume.{ext}")
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            if uploaded_file.type == "text/plain":
                extracted = uploaded_file.read().decode("utf-8")
            else:
                extracted = extract_skills_from_pdf(uploaded_file)
            skills_path = os.path.join(UPLOAD_DIR, f"{email}_skills.txt")
            with open(skills_path, "w", encoding="utf-8") as f:
                f.write(extracted)
            st.success("Resume uploaded and skills extracted!")
            extracted_skills = extracted  # Update local variable
    final_skills = extracted_skills
    if additional_skills:
        final_skills += ", " + additional_skills if final_skills else additional_skills
    final_location = location.strip()
    if st.button("Generate My Hustles"):
        if final_skills:
            with st.spinner("Generating personalized ideas..."):
                ideas = generate_hustles(final_skills, final_location)
            st.session_state.ideas_list = ideas.strip().split("\n\n")
            st.session_state.idea_index = 0
            st.session_state.liked_idea = None
            st.success("Ideas ready! Swipe to explore.")
            # Update free count
            if 'user_email' in st.session_state:
                email = st.session_state.user_email
                st.session_state.free_count += 1
                users[email]["free_count"] = st.session_state.free_count
                save_json("users.json", users)
            else:
                ip = get_ip()
                guests[ip] = guests.get(ip, 0) + 1
                save_json(GUESTS_FILE, guests)
        else:
            st.warning("Upload a resume or enter additional skills first.")
        # CLEAN SWIPE CARDS
        if 'ideas_list' in st.session_state and st.session_state.ideas_list:
            ideas_list = st.session_state.ideas_list
            index = st.session_state.idea_index
            if index < len(ideas_list):
                idea_text = ideas_list[index]
                # Render with centering for title
                idea_text = idea_text.replace('**', '<b>').replace('**', '</b>')
                st.markdown(f"""
                <div class="idea-card">
                    <h2>{idea_text.splitlines()[0]}</h2>
                    <p>{'<br>'.join(idea_text.splitlines()[1:])}</p>
                </div>
                """, unsafe_allow_html=True)
                col1, col2, col3 = st.columns([1, 2, 1])
                with col1:
                    if st.button("👎 Dislike", key=f"dislike_{index}"):
                        with st.spinner("Generating a new idea..."):
                            new = generate_single_hustle(final_skills, final_location)
                        st.session_state.ideas_list[index] = new
                        st.session_state.idea_index += 1
                        # Count swipe
                        if 'user_email' in st.session_state:
                            email = st.session_state.user_email
                            st.session_state.free_count += 1
                            users[email]["free_count"] = st.session_state.free_count
                            save_json("users.json", users)
                        else:
                            ip = get_ip()
                            guests[ip] = guests.get(ip, 0) + 1
                            save_json(GUESTS_FILE, guests)
                        st.rerun()
                with col3:
                    if st.button("❤️ Like", key=f"like_{index}"):
                        if 'user_email' in st.session_state:
                            email = st.session_state.user_email
                            path = os.path.join(CHECKLIST_DIR, f"{email}.json")
                            data = load_json(path, [])
                            new_entry = {"idea": idea_text, "checklist": generate_checklist(idea_text)}
                            data.append(new_entry)
                            save_json(path, data)
                            st.success("Saved to your Checklist!")
                        st.session_state.idea_index += 1
                        st.rerun()
            else:
                st.success("You've seen all ideas! Generate more or upgrade.")
# ----------------------------------------------------------------------
# Bottom Navigation
# ----------------------------------------------------------------------
st.markdown("""
<div class="bottom-nav">
    <a href="/Home" target="_self">Home</a>
    <a href="/Checklist" target="_self">Checklist</a>
    <a href="/Community" target="_self">Community</a>
    <a href="/Account" target="_self">Account</a>
    <a href="/Settings" target="_self">Settings</a>
</div>
""", unsafe_allow_html=True)