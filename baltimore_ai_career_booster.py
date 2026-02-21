import streamlit as st
import stripe
from groq import Groq
import PyPDF2
from datetime import datetime

st.set_page_config(page_title="Baltimore AI Career Booster", page_icon="🚀")
st.title("🚀 Baltimore AI Career Booster")
st.markdown("**Get hired faster at the Port, Johns Hopkins, Amazon, or city jobs — $29 lifetime**")

# ====================== SECRETS ======================
stripe.api_key = st.secrets["stripe"]["secret_key"]
GROQ_API_KEY = st.secrets["groq"]["api_key"]
client = Groq(api_key=GROQ_API_KEY)

model = "llama-3.3-70b-versatile"

# ====================== STATE ======================
if "paid" not in st.session_state:
    st.session_state.paid = False
if "free_uses" not in st.session_state:
    st.session_state.free_uses = 1
if "email" not in st.session_state:
    st.session_state.email = ""

# ====================== PAYMENT CHECK ======================
if "session_id" in st.query_params:
    try:
        session = stripe.checkout.Session.retrieve(st.query_params["session_id"][0])
        if session.payment_status == "paid":
            st.session_state.paid = True
            st.success("✅ Payment successful! Full access unlocked forever.")
    except:
        pass

# Free uses notice
if not st.session_state.paid:
    st.info(f"🎁 You have **{st.session_state.free_uses} free resume rewrites** left. Unlock unlimited for $29 lifetime.")

# ====================== PAY BUTTON (always visible if not paid) ======================
if not st.session_state.paid:
    if st.button("💰 Pay $29 for Lifetime Access", type="primary"):
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": "Baltimore AI Career Booster - Lifetime"},
                    "unit_amount": 2900,
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url="https://baltimore-career-booster-5yqmdnvotfjrjeg9xcm56l.streamlit.app/?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="https://baltimore-career-booster-5yqmdnvotfjrjeg9xcm56l.streamlit.app/",
        )
        st.link_button("Complete payment on Stripe", checkout_session.url)

    with st.expander("🔐 Admin Access"):
        admin_input = st.text_input("Admin password", type="password")
        if admin_input == st.secrets["admin"]["password"]:
            st.session_state.paid = True
            st.rerun()

# ====================== EMAIL CAPTURE (after payment) ======================
if st.session_state.paid and not st.session_state.email:
    st.subheader("One last step")
    email_input = st.text_input("Email for receipt & occasional AGI updates (optional)")
    if st.button("Save email"):
        st.session_state.email = email_input
        print(f"EMAIL_CAPTURED | {datetime.now().isoformat()} | {email_input}")
        st.success("Saved! Check your inbox for the Stripe receipt.")

# ====================== MAIN APP ======================
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
        messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_message}],
        temperature=0.7,
        max_tokens=2500,
    )
    return response.choices[0].message.content

# Resume rewrite (free sample allowed)
if st.button("🔄 Rewrite My Resume", type="primary"):
    if not resume_text or not job_title:
        st.error("Please upload resume and add job title")
    elif st.session_state.paid or st.session_state.free_uses > 0:
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

            # AUTO AGI TRAINING LOG
            print(f"AGI_TRAINING_DATA | {datetime.now().isoformat()} | action=resume | job_title={job_title} | company={company or 'N/A'} | free={not st.session_state.paid} | email={st.session_state.email or 'N/A'} | resume_chars={len(resume_text)}")

            if not st.session_state.paid:
                st.session_state.free_uses -= 1
                st.info(f"Free uses left: {st.session_state.free_uses}")
    else:
        st.error("No free uses left. Pay $29 for unlimited access.")

# Cover letter (paid only)
if st.button("✉️ Generate Cover Letter"):
    if st.session_state.paid:
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
                print(f"AGI_TRAINING_DATA | {datetime.now().isoformat()} | action=cover | job_title={job_title} | company={company or 'N/A'} | free=False | email={st.session_state.email or 'N/A'}")
    else:
        st.error("Cover letters require full access — unlock for $29 lifetime.")

# Interview prep (paid only)
if st.button("🎤 10 Interview Questions + Sample Answers"):
    if st.session_state.paid:
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
                print(f"AGI_TRAINING_DATA | {datetime.now().isoformat()} | action=interview | job_title={job_title} | company={company or 'N/A'} | free=False | email={st.session_state.email or 'N/A'}")
    else:
        st.error("Interview prep requires full access — unlock for $29 lifetime.")

st.caption("Built in Baltimore • Every use trains our AGI • Questions? DM me")
