import os
from dotenv import load_dotenv
import streamlit as st
from PyPDF2 import PdfReader
from docx import Document

# Optional: Google generative AI
try:
    from google import generativeai as genai
    GAI_AVAILABLE = True
except ImportError:
    GAI_AVAILABLE = False

# Load .env
load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if GAI_AVAILABLE and GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')
else:
    model = None

# --- File extraction functions ---
def extract_text_from_pdf(upload):
    reader = PdfReader(upload)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text
    return text

def extract_text_from_docx(upload):
    doc = Document(upload)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

# --- Streamlit UI ---
st.set_page_config(page_title="AI Resume Reviewer", page_icon="💼", layout="centered")

# Custom CSS for UI
st.markdown("""
<style>
.stFileUploader label div {
    color: white !important;
    font-weight: bold;
    background-color: #222222;
    border-radius: 10px;
    padding: 12px;
    border: 2px solid #FF69B4;
}
.stFileUploader button {
    background-color: #FF69B4 !important;
    color: white !important;
    font-weight: bold;
    border-radius: 8px !important;
    border: none !important;
}
.stFileUploader button:hover {
    background-color: #FF1493 !important;
}
h1 {
    color: #2E2E3A;
    text-align: center;
    font-weight: 800;
}
</style>
""", unsafe_allow_html=True)

st.title("AI RESUME REVIEWER")
st.write("By Vivansh")
st.write("Upload your Resume in PDF or DOCx format")

upload = st.file_uploader("Upload your file", type=['pdf', 'docx'])

if upload is not None:
    if upload.type == 'application/pdf':
        text = extract_text_from_pdf(upload)
    else:
        text = extract_text_from_docx(upload)

    st.header("Resume Analysis")
    
    if not GAI_AVAILABLE:
        st.warning("Google generative AI package not installed. Analysis will be simulated.")
        st.markdown("**Simulated analysis:**\n\n- Candidate Summary: TBD\n- Skills: TBD\n- Suggestions: TBD\n- Overall Rating: TBD")
    elif not GEMINI_API_KEY:
        st.warning("GEMINI_API_KEY missing. Please set it in .env file.")
    else:
        with st.spinner("Analyzing Your Resume..."):
            prompt = f"""
You are an expert Resume reviewer and a Recruiter.
Review the following Resume and provide:

1. Short summary of candidate
2. Key skills & improvement suggestions
3. Missing details
4. Key recruiter-focused insights
5. Overall rating (ATS)
6. Rewritten version of resume

Resume text:
{text}
"""
            try:
                response = model.generate_content(prompt)
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Error generating AI content: {e}")
