from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
import io
import base64
from PIL import Image
import pdf2image
import google.generativeai as genai

# Set up the Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to send inputs to Gemini and get the response
def analyze_resume_with_gemini(job_desc, resume_images, prompt_text):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content([job_desc, *resume_images, prompt_text])
        return response.text
    except Exception as error:
        return f"Gemini API error: {str(error)}"

# Convert PDF pages to images and prepare them for Gemini input
def process_pdf(uploaded_pdf):
    try:
        # Convert entire PDF to list of PIL images
        pages = pdf2image.convert_from_bytes(uploaded_pdf.read())

        image_parts = []
        for page in pages:
            buffer = io.BytesIO()
            page.save(buffer, format='JPEG')
            img_bytes = buffer.getvalue()
            encoded = base64.b64encode(img_bytes).decode()

            image_parts.append({
                "mime_type": "image/jpeg",
                "data": encoded
            })

        # Return image parts + first page for preview
        return image_parts, pages[0]
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return None, None

# Prompts for HR and ATS perspective
HR_PROMPT = """
You're acting as an experienced HR specialist with strong technical awareness.
Evaluate this resume against the job description: highlight where the candidate fits well,
where they fall short, and any key observations.
"""

ATS_PROMPT = """
You're simulating an ATS (Applicant Tracking System) and evaluating the resume against the job description.
Provide:
1. A percentage match
2. Any important keywords missing
3. Final summary thoughts
"""

# --- Streamlit app starts here ---

st.set_page_config(page_title="ATS Resume Analyzer", layout="wide")

st.title("📄 Resume ATS Analyzer")
st.write("This tool helps you evaluate how well your resume matches a job description using Gemini AI.")

# Sidebar help
with st.sidebar:
    st.subheader("How to Use")
    st.markdown("""
    1. Paste the job description  
    2. Upload your resume (PDF)  
    3. Click a button to get the analysis  
    4. Download the result if you like
    """)
    st.caption("Built with ❤️ by Vithusan.V")

# Job description input
job_description = st.text_area("Job Description", height=200)

# Upload resume
uploaded_resume = st.file_uploader("Upload your resume as PDF", type=["pdf"])

resume_ready = False
resume_images = None
first_page_preview = None

if uploaded_resume:
    st.success("Resume uploaded!")
    resume_images, first_page_preview = process_pdf(uploaded_resume)
    if resume_images:
        resume_ready = True
        st.image(first_page_preview, caption="First page of your resume", use_container_width=True)

# Buttons for analysis
col1, col2 = st.columns(2)
with col1:
    do_hr_eval = st.button("🔍 HR Review")
with col2:
    do_ats_eval = st.button("📊 ATS Match Score")

# Perform analysis if triggered
if (do_hr_eval or do_ats_eval) and not job_description:
    st.warning("Please enter a job description before analyzing.")

elif (do_hr_eval or do_ats_eval) and not resume_ready:
    st.warning("Please upload a resume PDF.")

elif (do_hr_eval or do_ats_eval):
    with st.spinner("Running analysis..."):
        selected_prompt = HR_PROMPT if do_hr_eval else ATS_PROMPT
        output = analyze_resume_with_gemini(job_description, resume_images, selected_prompt)

        st.subheader("🧠 Analysis Result")
        st.write(output)

        st.download_button(
            label="📥 Download Result",
            data=output,
            file_name="ats_resume_analysis.txt",
            mime="text/plain"
        )

# Footer at bottom
st.markdown("---")
st.markdown(
    '<div style="text-align:center; font-size:14px;">'
    '✅ Developed by <a href="https://github.com/thasvithu" target="_blank">Vithusan.V</a> | '
    '<a href="https://linkedin.com/in/thasvithu" target="_blank">LinkedIn</a>'
    '</div>',
    unsafe_allow_html=True
)
