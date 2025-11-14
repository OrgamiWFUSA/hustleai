import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

st.set_page_config(page_title="Account - HustleAI", layout="wide", initial_sidebar_state="collapsed")

# Enable back button navigation (fixes your swipe/backspace issue)
st.markdown('<style> section[data-testid="stSidebar"] { display: none !important; } </style>', unsafe_allow_html=True)
st.experimental_set_query_params()  # Allows browser back button

# Sign-in form
st.title("Sign In to HustleAI")
email = st.text_input("Email or Username")
password = st.text_input("Password", type="password")
if st.button("Sign In"):
    # Placeholder auth (expand with backend)
    st.session_state.user = email
    st.success("Signed in! Redirecting...")
    st.experimental_rerun()

st.markdown("New User? [Sign Up here](/signup)")

# Render bottom nav with active highlight
st.markdown(get_bottom_nav_html("account"), unsafe_allow_html=True)