import streamlit as st
from openai import OpenAI
import PyPDF2
import stripe
import os

# Set your OpenAI key here (get free from platform.openai.com/api-keys)
openai_key = os.environ.get("OPENAI_API_KEY", "sk-your-api-key-here")  # Replace with your full key

# Set your Stripe keys here (get from dashboard.stripe.com/apikeys)
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "sk_test_your-secret-key-here")  # Secret key (server-side)
publishable_key = os.environ.get("STRIPE_PUBLISHABLE_KEY", "pk_test_your-publishable-key-here")  # Publishable key (client-side)

def generate_hustles(skills):
    client = OpenAI(api_key=openai_key)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Generate 3 side hustle ideas for someone skilled in {skills}. Each idea should include: 1. Startup cost (under $100) 2. First month earnings potential ($100-$1000) 3. 3-step launch plan with specific actions. Format as numbered list with bold headings."}]
    )
    return response.choices[0].message.content

def extract_skills_from_pdf(pdf_file):
    text = ""
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    for page in pdf_reader.pages:
        text += page.extract_text()
    # Simple extraction (improve with NLP later)
    skills = text.lower()
    return skills[:500]  # Limit length

def generate_tiktok_script(ideas):
    client = OpenAI(api_key=openai_key)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Create a 15-second TikTok script for sharing these hustle ideas: {ideas}. Include hook, 3 ideas summary, call to action ('Try HustleAI!'), and hashtags."}]
    )
    return response.choices[0].message.content

st.title("🚀 HustleAI - AI Side Hustle Generator")
st.write("Upload resume or type your skills to get personalized ideas!")

# Freemium Paywall
if 'free_count' not in st.session_state:
    st.session_state.free_count = 0
if 'is_pro' not in st.session_state:
    st.session_state.is_pro = False

st.markdown(f"""
<script src="https://js.stripe.com/v3/"></script>
""", unsafe_allow_html=True)

if st.button("Upgrade to Pro ($4.99/month - unlimited ideas)"):
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'HustleAI Pro',
                    },
                    'unit_amount': 499,  # $4.99
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='http://localhost:8501?paid=true',
            cancel_url='http://localhost:8501',
        )
        st.components.v1.html(f"""
            <button id="checkout-button">Pay with Stripe</button>
            <script>
            var stripe = Stripe('{publishable_key}');
            var checkoutButton = document.getElementById('checkout-button');
            checkoutButton.addEventListener('click', function() {{
                stripe.redirectToCheckout({{ sessionId: '{session.id}' }});
            }});
            </script>
        """, height=50, width=300)
    except Exception as e:
        st.error(f"Error: {e}")

if st.query_params.get("paid", [False])[0] == "true":
    st.session_state.is_pro = True
    st.success("Upgraded to Pro! Unlimited generations.")

if st.session_state.free_count >= 3 and not st.session_state.is_pro:
    st.warning("Free limit reached (3 ideas/month). Upgrade for unlimited!")
    st.info("Pro: $4.99/month - unlimited ideas, priority AI, exclusive templates.")
else:
    uploaded_file = st.file_uploader("Upload resume (TXT/PDF)", type=['txt', 'pdf'])
    skills = st.text_input("Or enter skills manually (e.g., writing, design, marketing):")

    if uploaded_file is not None:
        if uploaded_file.type == "text/plain":
            skills = uploaded_file.read().decode("utf-8")
            st.success("TXT resume uploaded—skills extracted!")
        elif uploaded_file.type == "application/pdf":
            skills = extract_skills_from_pdf(uploaded_file)
            st.success("PDF resume uploaded—skills extracted!")
        else:
            st.warning("File type not supported—use TXT or PDF.")

    if st.button("Generate My Hustles"):
        if skills:
            with st.spinner("Generating your hustles..."):
                ideas = generate_hustles(skills)
            st.subheader("Your Personalized Hustle Ideas:")
            st.write(ideas)
            
            # Viral Share
            if st.button("Share on TikTok"):
                with st.spinner("Generating TikTok script..."):
                    script = generate_tiktok_script(ideas)
                st.subheader("TikTok Script Ready!")
                st.write(script)
                st.info("Copy the script, record a video, post with #HustleAI!")
            
            # Update free count
            if not st.session_state.is_pro:
                st.session_state.free_count += 1
                if st.session_state.free_count >= 3:
                    st.warning("Free limit reached—upgrade for more!")
        else:
            st.warning("Enter some skills or upload a resume to get started!")

# Community Forum (Simple MVP - user comments)
st.subheader("Community Forum: Share Your Wins!")
if 'comments' not in st.session_state:
    st.session_state.comments = []

new_comment = st.text_input("Share your hustle win or tip:")
if st.button("Post Comment"):
    if new_comment:
        st.session_state.comments.append(new_comment)
        st.success("Posted!")

for comment in st.session_state.comments:
    st.write(f"- {comment}")

st.sidebar.title("Monetization")
st.sidebar.write("Freemium: 3 free ideas/month, $4.99 for unlimited.")
st.sidebar.write("Affiliates: Shopify, Canva links.")