import streamlit as st
from openai import OpenAI
import PyPDF2
import stripe
import os
import json
from datetime import datetime, timedelta
# ----------------------------------------------------------------------
# PAGE CONFIG + ENABLE BACK BUTTON
# ----------------------------------------------------------------------
st.set_page_config(page_title="HustleAI", page_icon="rocket", layout="centered", initial_sidebar_state="expanded")
st.experimental_set_query_params(**st.experimental_get_query_params())
params = st.experimental_get_query_params()
if "logout" in params and params["logout"][0] == "true":
    if 'user_email' in st.session_state:
        del st.session_state.user_email
        del st.session_state.username
        del st.session_state.free_count
        del st.session_state.is_pro
    st.experimental_set_query_params(page="Home")
    st.rerun()
page = params.get("page", ["Home"])[0]
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
def load_json(path, default):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default
def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
users = load_json("users.json", {})
posts = load_json("posts.json", [])
# ----------------------------------------------------------------------
# GUEST TRACKING
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
# SKILL EXTRACTION FUNCTION
# ----------------------------------------------------------------------
def extract_skills_from_pdf(uploaded_file):
    # Extract all text from the PDF
    reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    
    # Convert text to lowercase for case-insensitive matching
    text_lower = text.lower()
    
    # List of common skills (compiled from resume best practices)
    common_skills = [
        "active listening", "communication", "computer skills", "customer service",
        "interpersonal skills", "leadership", "management", "problem-solving",
        "time management", "transferable skills", "verbal communication",
        "nonverbal communication", "written communication", "empathy",
        "emotional intelligence", "collaboration", "teamwork", "presentation skills",
        "negotiation", "conflict resolution", "adaptability", "creativity",
        "critical thinking", "organization", "attention to detail", "project management",
        "data analysis", "microsoft office", "excel", "powerpoint", "word",
        "google workspace", "programming", "python", "java", "sql", "javascript",
        "html", "css", "machine learning", "ai", "data science", "web development",
        "graphic design", "adobe creative suite", "photoshop", "illustrator",
        "sales", "marketing", "seo", "content creation", "social media management",
        "public speaking", "research", "analytical skills", "budgeting",
        "financial analysis", "accounting", "crm software", "salesforce",
        "networking", "multitasking", "initiative", "reliability", "work ethic"
    ]
    
    # Find matching skills in the text
    extracted_skills = [skill for skill in common_skills if skill.lower() in text_lower]
    
    # Remove duplicates and sort
    extracted_skills = sorted(set(extracted_skills))
    
    return ', '.join(extracted_skills)
# ----------------------------------------------------------------------
# AI FUNCTIONS — WITH LOCATION SUPPORT
# ----------------------------------------------------------------------
def generate_hustles(skills, location=""):
    location_prompt = f"in or near {location}" if location else "anywhere in the world"
    try:
        client = OpenAI(api_key=openai_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"Generate 3 side hustle ideas for someone skilled in {skills}, {location_prompt}. "
                                                  "For each idea, provide the full complete response in this exact format (do not output partial responses, and no 'Idea #1' prefix):\n"
                                                  "**Subject**\n"
                                                  "First Month Overhead: $X (under $100)\n"
                                                  "First Month Income Potential: $Y-$Z\n"
                                                  "· Bullet point 1 with more detail of the idea\n"
                                                  "· Bullet point 2 with more detail of the idea\n"
                                                  "· Bullet point 3 with more detail of the idea\n"
                                                  "· Bullet point 4 with more detail of the idea\n"
                                                  "3-step launch plan:\n"
                                                  "1. Step 1\n"
                                                  "2. Step 2\n"
                                                  "3. Step 3\n\n"
                                                  "Example:\n"
                                                  "**Freelance Graphic Design Services**\n"
                                                  "First Month Overhead: $50 (under $100)\n"
                                                  "First Month Income Potential: $300-$800\n"
                                                  "· Leverage your graphic design skills to create logos, banners, and social media graphics for small businesses.\n"
                                                  "· Target local startups or online entrepreneurs who need affordable design work.\n"
                                                  "· Use free tools like Canva initially, upgrading as needed.\n"
                                                  "· Offer packages starting at low rates to build a portfolio quickly.\n"
                                                  "3-step launch plan:\n"
                                                  "1. Build a simple portfolio on a free site like Behance.\n"
                                                  "2. Post services on freelance platforms like Upwork or Fiverr.\n"
                                                  "3. Network on social media and reach out to potential clients."}]
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"OpenAI error: {e}")
        return "Error generating ideas."
def generate_single_hustle(skills, location=""):
    location_prompt = f"in or near {location}" if location else "anywhere"
    try:
        client = OpenAI(api_key=openai_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"Generate 1 new side hustle idea for someone skilled in {skills}, {location_prompt}. "
                                                  "Provide the full complete response in this exact format (do not output partial responses, and no 'Idea #1' prefix):\n"
                                                  "**Subject**\n"
                                                  "First Month Overhead: $X (under $100)\n"
                                                  "First Month Income Potential: $Y-$Z\n"
                                                  "· Bullet point 1 with more detail of the idea\n"
                                                  "· Bullet point 2 with more detail of the idea\n"
                                                  "· Bullet point 3 with more detail of the idea\n"
                                                  "· Bullet point 4 with more detail of the idea\n"
                                                  "3-step launch plan:\n"
                                                  "1. Step 1\n"
                                                  "2. Step 2\n"
                                                  "3. Step 3\n"
                                                  "Example:\n"
                                                  "**Freelance Graphic Design Services**\n"
                                                  "First Month Overhead: $50 (under $100)\n"
                                                  "First Month Income Potential: $300-$800\n"
                                                  "· Leverage your graphic design skills to create logos, banners, and social media graphics for small businesses.\n"
                                                  "· Target local startups or online entrepreneurs who need affordable design work.\n"
                                                  "· Use free tools like Canva initially, upgrading as needed.\n"
                                                  "· Offer packages starting at low rates to build a portfolio quickly.\n"
                                                  "3-step launch plan:\n"
                                                  "1. Build a simple portfolio on a free site like Behance.\n"
                                                  "2. Post services on freelance platforms like Upwork or Fiverr.\n"
                                                  "3. Network on social media and reach out to potential clients."}]
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"OpenAI error: {e}")
        return "Error."
def generate_checklist(idea):
    try:
        client = OpenAI(api_key=openai_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"Break down this side hustle idea into a checklist of 5-10 goals with specific due dates (start from today, spread over 1 month). Format exactly as a numbered list like '1. Goal - YYYY-MM-DD' where due dates are in YYYY-MM-DD format."}]
        )
        txt = response.choices[0].message.content
        lines = txt.split('\n')
        goals = []
        for line in lines:
            if line.strip():
                parts = line.split(' - ')
                if len(parts) == 2:
                    goal = parts[0].strip()
                    due_str = parts[1].strip()
                    try:
                        # Validate and parse the date
                        due_date = datetime.strptime(due_str, '%Y-%m-%d')
                        goals.append({"goal": goal, "due": due_date.strftime('%Y-%m-%d')})
                    except ValueError:
                        # If invalid, use default
                        goals.append({"goal": goal, "due": (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')})
                else:
                    goals.append({"goal": line.strip(), "due": (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')})
        return goals
    except Exception as e:
        st.error(f"OpenAI error: {e}")
        return []
# ----------------------------------------------------------------------
# BEAUTIFUL DESIGN + LOGO + TOP HEADER
# ----------------------------------------------------------------------
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
    .header {background-color: #001f3f; padding: 10px; color: white; display: flex; justify-content: flex-end; align-items: center; width: 100%;}
    .header a {color: white; margin: 0 10px; text-decoration: none;}
    .header span {color: white; margin: 0 10px;}
</style>
""", unsafe_allow_html=True)

# Top Header
st.markdown("""
<div class="header">
    <a href="#">Email Preferences</a>
    <a href="#">Help Center</a> |
""", unsafe_allow_html=True)

if 'user_email' in st.session_state:
    st.markdown(f"""
    <span>{st.session_state.username}</span>
    <a href="?page=Settings">Settings</a>
    <a href="?logout=true">Log Out</a>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <a href="?page=Login">Log In</a>
    <a href="?page=Signup">Sign Up</a>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# Logo
try:
    st.image("logo.png", use_column_width=False, width=180)
except:
    pass
st.markdown("<h1 class='title'>HustleAI</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Turn your skills into side income — anywhere.</p>", unsafe_allow_html=True)
# ----------------------------------------------------------------------
# Navigation
# ----------------------------------------------------------------------
pages_nav = {
    "Home": "Generate Hustles",
    "Checklist": "My Checklist",
    "Community": "Community Forum",
    "Monetization": "Upgrade to Pro",
    "Settings": "Settings"
}
nav_col = st.sidebar.selectbox("Navigate", list(pages_nav.keys()))
if nav_col != page:
    st.experimental_set_query_params(page=nav_col)
    st.rerun()
# ----------------------------------------------------------------------
# Home – WITH LOCATION + CLEAN CARDS
# ----------------------------------------------------------------------
if page == "Home":
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
            st.experimental_set_query_params(page="Home")
            st.rerun()
        else:
            st.error("Invalid email or password.")
    st.write("New user?")
    if st.button("Sign Up Here"):
        st.experimental_set_query_params(page="Signup")
        st.rerun()
# ----------------------------------------------------------------------
# Signup
# ----------------------------------------------------------------------
elif page == "Signup":
    st.title("Sign Up to HustleAI")
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Sign Up"):
        if email not in users:
            users[email] = {"username": username, "password": password, "free_count": 0, "is_pro": False}
            save_json("users.json", users)
            st.session_state.user_email = email
            st.session_state.username = username
            st.session_state.free_count = 0
            st.session_state.is_pro = False
            st.success("Signed up successfully!")
            st.experimental_set_query_params(page="Home")
            st.rerun()
        else:
            st.error("Email already exists.")
    if st.button("Back to Login"):
        st.experimental_set_query_params(page="Login")
        st.rerun()
# ----------------------------------------------------------------------
# Community
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
# ----------------------------------------------------------------------
# Checklist
# ----------------------------------------------------------------------
elif page == "Checklist":
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
# ----------------------------------------------------------------------
# Monetization
# ----------------------------------------------------------------------
elif page == "Monetization":
    st.title("Monetization & Upgrade")
    st.write("Freemium: 3 free ideas/month, $4.99 for unlimited.")
    st.write("Affiliates: Shopify, Canva links.")
    st.markdown(f"<script src='https://js.stripe.com/v3/'></script>", unsafe_allow_html=True)
    if st.button("Upgrade to Pro ($4.99/month)"):
        pass # Add Stripe later
# ----------------------------------------------------------------------
# Settings
# ----------------------------------------------------------------------
elif page == "Settings":
    st.title("Settings")
    if 'user_email' in st.session_state:
        email = st.session_state.user_email
        st.subheader("Account Information")
        st.write(f"Username: {st.session_state.username}")
        st.write(f"Email: {email}")
        st.write(f"Subscription: {'Pro' if st.session_state.is_pro else 'Free'}")
        # Assuming no expiration date, add if needed
        # st.write(f"Subscription expires: {users[email].get('subscription_expiry', 'N/A')}")
        
        st.subheader("Change Password")
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        if st.button("Update Password"):
            if current_password == users[email]["password"]:
                if new_password == confirm_password and new_password:
                    users[email]["password"] = new_password
                    save_json("users.json", users)
                    st.success("Password updated!")
                else:
                    st.error("New passwords do not match or are empty.")
            else:
                st.error("Current password is incorrect.")
    else:
        st.warning("Sign in to access settings.")
