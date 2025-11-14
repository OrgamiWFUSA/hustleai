import streamlit as st
from ..utils import *  # Import shared functions

st.markdown(bottom_nav_css, unsafe_allow_html=True)

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