# --- Environment Setup ---
from dotenv import load_dotenv
load_dotenv()

# --- Imports ---
import streamlit as st
import os
import io
import base64
from PIL import Image
import pdf2image
import google.generativeai as genai

# --- Configure Gemini ---
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# --- Gemini Response Generator ---
def get_gemini_response(job_description, resume_parts, prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content([job_description, *resume_parts, prompt])
        return response.text
    except Exception as e:
        return f"❌ Gemini Error: {str(e)}"

# --- PDF to Image Conversion (Multi-page support) ---
def convert_pdf_to_images(uploaded_file):
    try:
        images = pdf2image.convert_from_bytes(uploaded_file.read())
        img_bytes_list = []
        for page in images:
            img_io = io.BytesIO()
            page.save(img_io, format='JPEG')
            img_data = base64.b64encode(img_io.getvalue()).decode()
            img_bytes_list.append({
                "mime_type": "image/jpeg",
                "data": img_data
            })
        return img_bytes_list, images[0]  # Return all pages + preview of first page
    except Exception as e:
        st.error(f"⚠️ Error converting PDF: {e}")
        return None, None

# --- Prompts ---
HR_EVALUATION_PROMPT = """
You are an experienced HR with deep technical knowledge in roles such as Data Scientist, Full Stack Developer,
Big Data Engineer, DevOps Engineer, or Data Analyst. Evaluate the following resume against the provided job description.
Provide a summary of strengths, weaknesses, and role alignment.
"""

ATS_MATCH_PROMPT = """
You are a skilled ATS system trained to evaluate resumes. Analyze this resume against the job description.
Provide:
1. A percentage match
2. Missing keywords/skills
3. Final recommendations
"""

# --- Streamlit UI ---
st.set_page_config(page_title="AI-Powered ATS Resume Analyzer", layout="wide")
st.title("📄 AI-Powered ATS Resume Analyzer")
st.markdown("Use Google Gemini to analyze your resume against any job description.")

# --- Sidebar Help ---
with st.sidebar:
    st.header("📌 Instructions")
    st.markdown("""
    1. Paste the **job description**.
    2. Upload your **resume (PDF)**.
    3. Click **analyze** to get a Gemini-powered evaluation.
    4. Optionally download results as a `.txt` report.
    """)
    st.markdown("---")
    st.caption("💡 Developed by **Vithusan.V**")

# --- Inputs ---
input_text = st.text_area("📝 Paste Job Description Here", height=200)
uploaded_file = st.file_uploader("📎 Upload Resume (PDF Only)", type=["pdf"])

if uploaded_file:
    st.success("✅ Resume uploaded!")
    resume_parts, preview_image = convert_pdf_to_images(uploaded_file)

    if preview_image:
        st.image(preview_image, caption="📄 First Page Preview", use_container_width=True)

# --- Buttons ---
col1, col2 = st.columns(2)
with col1:
    submit_hr = st.button("🔍 HR Perspective")
with col2:
    submit_ats = st.button("📊 ATS Match Score")

# --- Evaluation Logic ---
if (submit_hr or submit_ats) and not input_text:
    st.error("⚠️ Please enter a job description.")

if (submit_hr or submit_ats) and not uploaded_file:
    st.error("⚠️ Please upload a PDF resume.")

if (submit_hr or submit_ats) and uploaded_file and input_text:
    with st.spinner("🔎 Analyzing with Gemini..."):
        selected_prompt = HR_EVALUATION_PROMPT if submit_hr else ATS_MATCH_PROMPT
        result = get_gemini_response(input_text, resume_parts, selected_prompt)
        st.subheader("📬 Gemini Evaluation")
        st.write(result)

        # --- Download Option ---
        st.download_button(
            label="📥 Download Analysis as TXT",
            data=result,
            file_name="resume_analysis.txt",
            mime="text/plain"
        )

# --- Footer ---
st.markdown("---")
st.markdown("✅ **Developed by [Vithusan.V](github.com/thasvithu)**")
