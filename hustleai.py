import streamlit as st
from openai import OpenAI
import PyPDF2
import stripe
import os
import json
from datetime import datetime, timedelta

# ----------------------------------------------------------------------
# OPENAI KEY - MUST MATCH SECRET NAME EXACTLY
# ----------------------------------------------------------------------
try:
    openai_key = st.secrets["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"]
except:
    st.error("OpenAI API key not found in secrets. Add it in Streamlit Cloud → Settings → Secrets")
    st.stop()

# ----------------------------------------------------------------------
# STRIPE KEYS
# ----------------------------------------------------------------------
stripe.api_key = st.secrets.get("STRIPE_SECRET_KEY", "sk_test_...")
publishable_key = st.secrets.get("STRIPE_PUBLISHABLE_KEY", "pk_test_...")

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
# AI Functions
# ----------------------------------------------------------------------
def generate_hustles(skills):
    client = OpenAI(api_key=openai_key)
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user",
                   "content": f"Generate 3 side hustle ideas for someone skilled in {skills}. "
                              "Each idea must include: 1. Startup cost (under $100) 2. First month earnings potential ($100-$1000) "
                              "3. 3-step launch plan. Format as numbered list with bold headings."}]
    )
    return resp.choices[0].message.content

def generate_single_hustle(skills):
    client = OpenAI(api_key=openai_key)
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user",
                   "content": f"Generate 1 side hustle idea for someone skilled in {skills}. "
                              "Include: 1. Startup cost (under $100) 2. First month earnings potential ($100-$1000) "
                              "3. 3-step launch plan. Format with bold headings."}]
    )
    return resp.choices[0].message.content

def extract_skills_from_pdf(pdf_file):
    text = ""
    reader = PyPDF2.PdfReader(pdf_file)
    for page in reader.pages:
        text += page.extract_text()
    return text.lower()[:500]

def generate_checklist(idea):
    client = OpenAI(api_key=openai_key)
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user",
                   "content": f"Break down this side hustle idea into a checklist of 5-10 goals with specific due dates "
                              "(start from today, spread over 1 month). Format as numbered list with editable due dates."}]
    )
    txt = resp.choices[0].message.content
    lines = txt.split('\n')
    goals = []
    for line in lines:
        if line.strip():
            parts = line.split(' - ')
            goal = parts[0]
            due = parts[1] if len(parts) > 1 else (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
            goals.append({"goal": goal, "due": due})
    return goals

# ----------------------------------------------------------------------
# Styling
# ----------------------------------------------------------------------
st.markdown("""
<style>
.stApp {background-color:#f0f2f6;}
.stButton>button{background:#4CAF50;color:#fff;padding:10px 20px;border-radius:5px;}
.stButton>button:hover{background:#45a049;}
.stTextInput>div>div>div{background:#fff;border:1px solid #ddd;border-radius:5px;}
.stSidebar .stSidebarContent{background:#e0e0e0;}
.stExpander{border:1px solid #ddd;border-radius:5px;padding:10px;margin-bottom:10px;}
</style>
""", unsafe_allow_html=True)

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
# Home – RESUME SAVED PER USER
# ----------------------------------------------------------------------
if page == "Home":
    st.title("HustleAI – AI Side Hustle Generator")
    st.write("Upload a resume or type your skills to get personalized ideas!")

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
            else:
                st.warning("Enter skills or upload a resume first.")

        if 'ideas_list' in st.session_state:
            lst = st.session_state.ideas_list
            idx = st.session_state.idea_index
            if idx < len(lst):
                st.subheader(f"Idea {idx+1}")
                st.write(lst[idx])
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Swipe Left (Dislike)"):
                        new = generate_single_hustle(final_skills)
                        st.session_state.ideas_list[idx] = new
                        st.success("New idea generated!")
                with c2:
                    if st.button("Swipe Right (Like)"):
                        st.session_state.liked_idea = lst[idx]
                        if 'user_email' in st.session_state:
                            email = st.session_state.user_email
                            path = os.path.join(CHECKLIST_DIR, f"{email}.json")
                            data = {"idea": lst[idx], "checklist": generate_checklist(lst[idx])}
                            save_json(path, data)
                            st.success("Checklist saved!")
                        st.success("Liked! See the Checklist page.")
            else:
                st.info("No more ideas – generate a new batch or upgrade.")

    if not st.session_state.is_pro and 'ideas_list' in st.session_state:
        st.session_state.free_count += 1
        if st.session_state.free_count >= 3:
            st.warning("Free limit reached – upgrade for more!")

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
    if 'user_email' not in st.session_state:
        st.warning("Sign in to view your checklist.")
    else:
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