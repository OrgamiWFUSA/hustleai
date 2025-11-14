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
st.markdown("<h1 class='title'>Settings</h1>", unsafe_allow_html=True)

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

# Bottom Navigation
st.markdown(bottom_nav_html, unsafe_allow_html=True)