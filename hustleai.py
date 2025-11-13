import streamlit as st
from openai import OpenAI
import PyPDF2
import stripe
import os
import json
from datetime import datetime, timedelta

# ----------------------------------------------------------------------
# OPENAI KEY - FROM SECRETS ONLY
# ----------------------------------------------------------------------
if "OPENAI_API_KEY" not in st.secrets:
    st.error("OPENAI_API_KEY missing! Add it in Streamlit Cloud → Settings → Secrets")
    st.stop()
openai_key = st.secrets["OPENAI_API_KEY"]

# ----------------------------------------------------------------------
# STRIPE KEYS
# ----------------------------------------------------------------------
stripe.api_key = st.secrets.get("STRIPE_SECRET_KEY", "")
publishable_key = st.secrets.get("STRIPE_PUBLISHABLE_KEY", "")

# ----------------------------------------------------------------------
# FOLDERS
# ----------------------------------------------------------------------
UPLOAD_DIR = "uploads"
CHECKLIST_DIR = "checklists"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CHECKLIST_DIR, exist_ok=True)

# ----------------------------------------------------------------------
# JSON HELPERS
# ----------------------------------------------------------------------
def load_json(path, default):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# ----------------------------------------------------------------------
# LOAD DATA ON EVERY RUN
# ----------------------------------------------------------------------
users = load_json("users.json", {})
posts = load_json("posts.json", [])

# ----------------------------------------------------------------------
# GUEST TRACKING (IP-based)
# ----------------------------------------------------------------------
GUESTS_FILE = "guests.json"
guests = load_json(GUESTS_FILE, {})

def get_ip():
    try:
        return st.context.headers.get("X-Forwarded-For", "unknown").split(',')[0].strip()
    except:
        return "unknown"

if "ip" not in st.session_state:
    st.session_state.ip = get_ip()

# ----------------------------------------------------------------------
# AI FUNCTIONS — WITH ERROR HANDLING
# ----------------------------------------------------------------------
def generate_hustles(skills):
    try:
        client = OpenAI(api_key=openai_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": f"Generate 3 side hustle ideas for someone skilled in {skills}. Each idea should include: 1. Startup cost (under $100) 2. First month earnings potential ($100-$1000) 3. 3-step launch plan with specific actions. Format as numbered list with bold headings."}]
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"OpenAI error: {e}")
        return "Error generating ideas."

def generate_single_hustle(skills):
    try:
        client = OpenAI(api_key=openai_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": f"Generate 1 side hustle idea for someone skilled in {skills}. Include: 1. Startup cost (under $100) 2. First month earnings potential ($100-$1000) 3. 3-step launch plan with specific actions. Format with bold headings."}]
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"OpenAI error: {e}")
        return "Error."

def generate_checklist(idea):
    try:
        client = OpenAI(api_key=openai_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": f"Break down this side hustle idea into a checklist of 5-10 goals with specific due dates (start from today, spread over 1 month). Format as numbered list with editable due dates."}]
        )
        txt = response.choices[0].message.content
        lines = txt.split('\n')
        goals = []
        for line in lines:
            if line.strip():
                parts = line.split(' - ')
                goal = parts[0]
                due = parts[1] if len(parts) > 1 else (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
                goals.append({"goal": goal, "due": due})
        return goals
    except Exception as e:
        st.error(f"OpenAI error: {e}")
        return []

# ----------------------------------------------------------------------
# BEAUTIFUL DESIGN + LOGO
# ----------------------------------------------------------------------
st.set_page_config(page_title="HustleAI", page_icon="rocket", layout="centered")

st.markdown("""
<style>
    .main {background: linear-gradient(135deg, #e0f7fa, #ffffff); padding: 2rem; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);}
    .logo {display: block; margin: 0 auto 1rem auto; max-width: 180px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);}
    .title {font-size: 2.8rem; font-weight: 700; text-align: center; color: #1565c0; margin-bottom: 0.5rem;}
    .subtitle {text-align: center; color: #555; font-size: 1.1rem; margin-bottom: 2rem;}
    .stButton>button {background: linear-gradient(45deg, #42a5f5, #1976d2); color: white; border: none; padding: 0.6rem 1.5rem; border-radius: 25px; font-weight: 600; box-shadow: 0 3px 8px rgba(0,0,0,0.2); transition: all 0.3s;}
    .stButton>button:hover {transform: translateY(-2px); box-shadow: 0 6px 12px rgba(0,0,0,0.3);}
    .stTextInput>div>div>input {border-radius: 12px; border: 1px solid #90caf9; padding: 0.8rem;}
    .stFileUploader>div>div {border-radius: 12px; border: 2px dashed #42a5f5; padding: 1rem;}
    .stExpander {background: white; border-radius: 12px; border: 1px solid #bbdefb; margin-bottom: 1rem;}
    .stSuccess {background: #e8f5e8; color: #2e7d32; border-radius: 12px; padding: 0.8rem;}
    .stWarning {background: #fff3e0; color: #f57c00; border-radius: 12px; padding: 0.8rem;}
    .idea-card {background:white; padding:2rem; border-radius:15px; box-shadow:0 8px 25px rgba(0,0,0,0.1); text-align:center; margin:1rem 0;}
</style>
""", unsafe_allow_html=True)

# Logo
try:
    st.image("logo.png", use_column_width=False, width=180)
except:
    st.markdown("<h1 class='title'>HustleAI</h1>", unsafe_allow_html=True)
else:
    st.markdown("<h1 class='title'>HustleAI</h1>", unsafe_allow_html=True)

st.markdown("<p class='subtitle'>Turn your skills into side income — in seconds.</p>", unsafe_allow_html=True)

# ----------------------------------------------------------------------
# Navigation
# ----------------------------------------------------------------------
pages = {
    "Home": "Generate Hustles",
    "Login": "Sign In",
    "Checklist": "My Checklist",
    "Community": "Community Forum",
    "Monetization": "Upgrade to Pro"
}
page = st.sidebar.selectbox("Navigate", list(pages.keys()))

if 'free_count' not in st.session_state: st.session_state.free_count = 0
if 'is_pro' not in st.session_state: st.session_state.is_pro = False

# ----------------------------------------------------------------------
# Home – generator + swipe + RESUME SAVED PER USER
# ----------------------------------------------------------------------
if page == "Home":
    # GUEST LIMIT
    if 'user_email' not in st.session_state:
        ip = get_ip()
        if guests.get(ip, 0) >= 3:
            st.warning("Free limit reached (3 ideas). Sign up to continue!")
            st.stop()

    # Load saved skills
    skills = ""
    if 'user_email' in st.session_state:
        email = st.session_state.user_email
        skills_path = os.path.join(UPLOAD_DIR, f"{email}_skills.txt")
        if os.path.exists(skills_path):
            with open(skills_path, "r", encoding="utf-8") as f:
                skills = f.read()
            st.success("Skills loaded from your saved resume!")

    if st.session_state.free_count >= 3 and not st.session_state.is_pro:
        st.warning("Free limit reached (3 ideas/month). Upgrade for unlimited!")
        st.info("Pro: $4.99/month – unlimited ideas, priority AI, exclusive templates.")
    else:
        uploaded_file = st.file_uploader("Upload resume (TXT/PDF)", type=['txt', 'pdf'])
        skills_input = st.text_input("Or enter skills manually:", value=skills)

        # SAVE RESUME + SKILLS
        if uploaded_file:
            if 'user_email' not in st.session_state:
                st.error("Sign in to save resume.")
            else:
                email = st.session_state.user_email
                ext = uploaded_file.name.split('.')[-1]
                file_path = os.path.join(UPLOAD_DIR, f"{email}_resume.{ext}")
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                # Extract skills
                if uploaded_file.type == "text/plain":
                    extracted = uploaded_file.read().decode("utf-8")
                else:
                    extracted = extract_skills_from_pdf(uploaded_file)
                skills_path = os.path.join(UPLOAD_DIR, f"{email}_skills.txt")
                with open(skills_path, "w", encoding="utf-8") as f:
                    f.write(extracted)
                st.success("Resume + skills saved!")

        final_skills = skills_input or (extracted if 'extracted' in locals() else "")
        if st.button("Generate My Hustles"):
            if final_skills:
                with st.spinner("Generating…"):
                    ideas = generate_hustles(final_skills)
                st.session_state.ideas_list = ideas.split('\n\n')
                st.session_state.idea_index = 0
                st.session_state.liked_idea = None
                st.success("Ideas ready! Swipe left/right.")

                # Update free count
                if 'user_email' in st.session_state:
                    email = st.session_state.user_email
                    users[email]["free_count"] = users[email].get("free_count", 0) + 1
                    save_json("users.json", users)
                    st.session_state.free_count = users[email]["free_count"]
                else:
                    ip = get_ip()
                    guests[ip] = guests.get(ip, 0) + 1
                    save_json(GUESTS_FILE, guests)
            else:
                st.warning("Enter skills or upload a resume first.")

        # FAST MOBILE SWIPE
        if 'ideas_list' in st.session_state:
            ideas_list = st.session_state.ideas_list
            index = st.session_state.idea_index
            if index < len(ideas_list):
                idea = ideas_list[index]

                st.markdown(f"""
                <div class="idea-card">
                    <h2>Idea {index + 1}</h2>
                    <div style="font-size:1.1rem;line-height:1.8;">{idea.replace('**', '<b>').replace('**', '</b>')}</div>
                </div>
                """, unsafe_allow_html=True)

                col1, col2, col3 = st.columns([1, 2, 1])
                with col1:
                    if st.button("👎 Dislike", key=f"dislike_{index}"):
                        new_idea = generate_single_hustle(final_skills)
                        st.session_state.ideas_list[index] = new_idea
                        st.session_state.idea_index += 1
                        # Update free count
                        if 'user_email' in st.session_state:
                            email = st.session_state.user_email
                            users[email]["free_count"] = users[email].get("free_count", 0) + 1
                            save_json("users.json", users)
                        else:
                            ip = get_ip()
                            guests[ip] = guests.get(ip, 0) + 1
                            save_json(GUESTS_FILE, guests)
                        st.rerun()

                with col3:
                    if st.button("❤️ Like", key=f"like_{index}"):
                        st.session_state.liked_idea = idea
                        if 'user_email' in st.session_state:
                            email = st.session_state.user_email
                            path = os.path.join(CHECKLIST_DIR, f"{email}.json")
                            data = {"idea": idea, "checklist": generate_checklist(idea)}
                            save_json(path, data)
                            st.success("Saved to your Checklist!")
                        st.session_state.idea_index += 1
                        st.rerun()

            else:
                st.success("You've seen all ideas! Generate more or upgrade.")

# ----------------------------------------------------------------------
# Login
# ----------------------------------------------------------------------
elif page == "Login":
    st.title("Sign In to HustleAI")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Sign In"):
        if email in users and users[email]["password"] == password:
            st.session_state.user_email = email
            st.session_state.username = users[email]["username"]
            st.session_state.free_count = users[email].get("free_count", 0)
            st.session_state.is_pro = users[email].get("is_pro", False)
            st.success(f"Signed in as {st.session_state.username}!")
        else:
            st.error("Invalid email or password.")
    st.write("New user?")
    if st.button("Sign Up Here"):
        st.switch_page("pages/_signup.py")

# ----------------------------------------------------------------------
# Community – nested replies
# ----------------------------------------------------------------------
elif page == "Community":
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
                    indent = "  " * depth
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

# ----------------------------------------------------------------------
# Checklist
# ----------------------------------------------------------------------
elif page == "Checklist":
    st.title("My Checklist")
    if 'user_email' in st.session_state:
        email = st.session_state.user_email
        path = os.path.join(CHECKLIST_DIR, f"{email}.json")
        if os.path.exists(path):
            data = load_json(path, {})
            st.subheader("Your Liked Hustle")
            st.write(data["idea"])
            st.subheader("Checklist")
            checklist = data.get("checklist", [])
            for i, item in enumerate(checklist):
                c1, c2 = st.columns([3,1])
                with c1: st.write(item["goal"])
                with c2:
                    new_date = st.date_input("Due", value=datetime.strptime(item["due"], '%Y-%m-%d'), key=f"due_{i}")
                    checklist[i]["due"] = new_date.strftime('%Y-%m-%d')
            if st.button("Save Changes"):
                save_json(path, {"idea": data["idea"], "checklist": checklist})
                st.success("Checklist updated!")
        else:
            st.info("No checklist yet – generate ideas and swipe right on one.")
    else:
        st.warning("Sign in to view your checklist.")

# ----------------------------------------------------------------------
# Monetization
# ----------------------------------------------------------------------
elif page == "Monetization":
    st.title("Monetization & Upgrade")
    st.write("Freemium: 3 free ideas/month, $4.99 for unlimited.")
    st.write("Affiliates: Shopify, Canva links.")
    st.markdown(f"<script src='https://js.stripe.com/v3/'></script>", unsafe_allow_html=True)
    if st.button("Upgrade to Pro ($4.99/month)"):
        pass  # Add Stripe later