import streamlit as st
import stripe
from groq import Groq
import PyPDF2

st.set_page_config(page_title="Baltimore AI Career Booster", page_icon="🚀")
st.title("🚀 Baltimore AI Career Booster")
st.markdown("**Get hired faster at the Port, Johns Hopkins, Amazon, or city jobs — $19 lifetime**")

# ====================== SECRETS (hidden) ======================
stripe.api_key = st.secrets["stripe"]["secret_key"]
GROQ_API_KEY = st.secrets["groq"]["api_key"]
client = Groq(api_key=GROQ_API_KEY)

model = "llama-3.3-70b-versatile"

# ====================== PAYMENT CHECK ======================
if "paid" not in st.session_state:
    st.session_state.paid = False

# Check for successful payment return
if "session_id" in st.query_params:
    try:
        session = stripe.checkout.Session.retrieve(st.query_params["session_id"][0])
        if session.payment_status == "paid":
            st.session_state.paid = True
            st.success("✅ Payment successful! Full access unlocked forever.")
    except:
        pass

# ====================== PAYWALL ======================
if not st.session_state.paid:
    st.warning("🔒 Full access unlocked after one-time $19 payment")

    if st.button("💰 Pay $19 for Lifetime Access", type="primary"):
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": "Baltimore AI Career Booster - Lifetime"},
                    "unit_amount": 1900,
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=f"https://YOUR-APP-NAME.streamlit.app/?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"https://YOUR-APP-NAME.streamlit.app/",
        )
        st.link_button("Complete payment on Stripe", checkout_session.url)

    with st.expander("🔐 Admin Access"):
        admin_input = st.text_input("Admin password", type="password")
        if admin_input == st.secrets["admin"]["password"]:
            st.session_state.paid = True
            st.rerun()

    st.stop()  # Stops here until paid

# ====================== FULL APP (paid users only) ======================
uploaded_file = st.file_uploader("Upload your resume (PDF or TXT)", type=["pdf", "txt"])
resume_text = st.text_area("Your resume text (edit if needed)", height=300)

col1, col2 = st.columns(2)
job_title = col1.text_input("Target Job Title", placeholder="Logistics Coordinator - Port of Baltimore")
company = col2.text_input("Company (optional)", placeholder="Port of Baltimore")

job_desc = st.text_area("Paste full Job Description (optional but recommended)", height=150)

SYSTEM_PROMPT = """You are an expert Baltimore Career Coach with 15+ years helping locals land jobs at the Port of Baltimore, Johns Hopkins Medicine, Amazon fulfillment centers, Fort Meade defense contractors, Maryland biotech firms, city government, and more.

You know exactly what hiring managers in Baltimore want, local keywords that beat ATS systems, Maryland pay ranges, and how to make resumes stand out here.

Be encouraging, honest, and laser-focused on Baltimore/Maryland opportunities. Use powerful action verbs and achievement-focused bullets."""

def call_groq(user_message):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        temperature=0.7,
        max_tokens=2500,
    )
    return response.choices[0].message.content

# Resume button
if st.button("🔄 Rewrite My Resume", type="primary"):
    if not resume_text or not job_title:
        st.error("Please upload resume and add job title")
    else:
        with st.spinner("Optimizing for Baltimore jobs..."):
            prompt = f"""Rewrite this resume to be perfectly tailored and ATS-optimized for the job below.
Make bullet points achievement-focused, add Baltimore/Maryland keywords, and make it sound professional.

RESUME:
{resume_text}

TARGET JOB: {job_title} at {company or 'a Baltimore employer'}

JOB DESCRIPTION:
{job_desc or 'General local opportunity'}

Output ONLY the full rewritten resume in clean markdown format with sections: Contact Info, Professional Summary, Experience, Skills, Education."""

            result = call_groq(prompt)
            st.markdown("### 🎉 Your Baltimore-Optimized Resume")
            st.markdown(result)
            st.download_button("📥 Download Resume", result, "optimized_resume.md")

# Cover Letter button
if st.button("✉️ Generate Cover Letter"):
    if not resume_text or not job_title:
        st.error("Please upload resume and add job title")
    else:
        with st.spinner("Writing cover letter..."):
            prompt = f"""Write a short, powerful, human-sounding cover letter (3-4 paragraphs) for this Baltimore job.

RESUME:
{resume_text}

TARGET JOB: {job_title} at {company or 'a Baltimore employer'}

JOB DESCRIPTION:
{job_desc or 'General local opportunity'}

Make it specific to Baltimore, show enthusiasm, and mention why the candidate is a great fit for this local role."""

            result = call_groq(prompt)
            st.markdown("### 📬 Your Custom Cover Letter")
            st.markdown(result)
            st.download_button("📥 Download Cover Letter", result, "cover_letter.md")

# Interview button
if st.button("🎤 10 Interview Questions + Sample Answers"):
    if not resume_text or not job_title:
        st.error("Please upload resume and add job title")
    else:
        with st.spinner("Preparing interview prep..."):
            prompt = f"""Create 10 likely interview questions for this Baltimore job + strong sample answers based on the resume.

RESUME:
{resume_text}

TARGET JOB: {job_title} at {company or 'a Baltimore employer'}

JOB DESCRIPTION:
{job_desc or 'General local opportunity'}

Format as numbered list with question then "Sample Strong Answer:" """

            result = call_groq(prompt)
            st.markdown("### 🏆 Interview Prep")
            st.markdown(result)

st.caption("Built in Baltimore • Every use trains our AGI • Questions? DM me")
