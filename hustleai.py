import streamlit as st
from utils import load_json, save_json, get_ip, extract_skills_from_pdf, generate_hustles, generate_single_hustle, generate_checklist, bottom_nav

# Page config
st.set_page_config(page_title="HustleAI", page_icon="rocket", layout="centered", initial_sidebar_state="expanded")

# Query params (moved early to fix NameError)
params = st.experimental_get_query_params()

# Logout handling
if "logout" in params and params["logout"][0] == "true":
    if 'user_email' in st.session_state:
        del st.session_state.user_email
        del st.session_state.username
        del st.session_state.free_count
        del st.session_state.is_pro
    st.experimental_set_query_params(page="Home")
    st.rerun()

# Bottom nav
bottom_nav()

# Header
st.markdown("""
<style>
    .main {background: linear-gradient(135deg, #e0f7fa, #ffffff); padding: 2rem; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);}
    .logo {display: block; margin: 0 auto 1rem auto; max-width: 180px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);}
    .title {font-size: 2.8rem; font-weight: 700; text-align: center; color: #1565c0; margin-bottom: 0.5rem; font-family: Arial, sans-serif;}
    .subtitle {text-align: center; color: #555; font-size: 1.1rem; margin-bottom: 2rem;}
    .stButton>button {background: linear-gradient(45deg, #42a5f5, #1976d2); color: white; border: none; padding: 0.8rem 2rem; border-radius: 30px; font-weight: 600; box-shadow: 0 4px 15px rgba(0,0,0,0.2);}
    .stButton>button:hover {transform: translateY(-3px); box-shadow: 0 8px 20px rgba(0,0,0,0.3);}
    .stTextInput>div>div>input {border-radius: 12px; border: 1px solid #90caf9; padding: 0.8rem;}
    .stFileUploader>div>div {border-radius: 12px; border: 2px dashed #42a5f5; padding: 1rem;}
    .idea-card {background:white; padding:2rem; border-radius:20px; box-shadow:0 10px 30px rgba(0,0,0,0.15); text-align:left; margin:1.5rem 0; border-left: 6px solid #42a5f5; font-family: Arial, sans-serif;}
    .idea-card h2 {text-align: center; font-weight: bold;}
    .bottom-nav {position: fixed; bottom: 0; left: 0; right: 0; background-color: #001f3f; padding: 10px; color: white; display: flex; justify-content: space-around; align-items: center; z-index: 1000; box-shadow: 0 -2px 5px rgba(0,0,0,0.2);}
    .bottom-nav a {color: white; text-decoration: none; font-size: 1rem; padding: 5px 10px;}
</style>
""", unsafe_allow_html=True)

try:
    st.image("logo.png", use_column_width=False, width=180)
except:
    pass
st.markdown("<h1 class='title'>HustleAI</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Turn your skills into side income — anywhere.</p>", unsafe_allow_html=True)

# Sidebar nav
pages_nav = {
    "Home": "Generate Hustles",
    "Checklist": "My Checklist",
    "Community": "Community Forum",
    "Account": "Account",
    "Settings": "Settings"
}
nav_col = st.sidebar.selectbox("Navigate", list(pages_nav.keys()))
if nav_col != params.get("page", ["Home"])[0]:
    st.experimental_set_query_params(page=nav_col)
    st.rerun()

# Guest tracking
if 'ip' not in st.session_state:
    st.session_state.ip = get_ip()

# Home logic (full from your original)
guests = load_json("guests.json", {})
users = load_json("users.json", {})
if 'user_email' not in st.session_state:
    if guests.get(st.session_state.ip, 0) >= 3:
        st.warning("Free limit reached (3 ideas). Sign up to continue!")
        st.stop()
else:
    if 'free_count' not in st.session_state:
        st.session_state.free_count = users[st.session_state.user_email].get("free_count", 0)
    if 'is_pro' not in st.session_state:
        st.session_state.is_pro = users[st.session_state.user_email].get("is_pro", False)

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
            extracted_skills = extracted
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
                ip = st.session_state.ip
                guests[ip] = guests.get(ip, 0) + 1
                save_json("guests.json", guests)
        else:
            st.warning("Upload a resume or enter additional skills first.")
    # CLEAN SWIPE CARDS
    if 'ideas_list' in st.session_state and st.session_state.ideas_list:
        ideas_list = st.session_state.ideas_list
        index = st.session_state.idea_index
        if index < len(ideas_list):
            idea_text = ideas_list[index]
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
                        ip = st.session_state.ip
                        guests[ip] = guests.get(ip, 0) + 1
                        save_json("guests.json", guests)
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