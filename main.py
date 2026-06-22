import streamlit as st
from openai import OpenAI
import PyPDF2
import io
import os
import re
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="📃CVForge AI", page_icon="📃", layout="centered")

st.title("📃CVForge AI")
st.markdown("CVForge AI is your new career companion designed to transform ordinary CVs and Resumes into recruiter ready, ATS optimized documents.")
st.markdown("""
📄 Upload your CV or Resume and receive instant insights, including:
            
• ATS Score Analysis  
• Job Match Evaluation  
• Strengths & Weaknesses Assessment  
• Missing Keyword Detection  
• Personalized Improvement Recommendations  

🎯 Designed to help you stand out in today's competitive job market and increase your chances of landing interviews.
""")
st.markdown("💼 No matter where you are in your career journey, CVForge AI provides data driven analysis, personalized recommendations, and ATS optimization to help you get noticed, get shortlisted, and get hired.")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

upload_file = st.file_uploader("upload your CV or Resume (PDF or TXT)", type=["pdf", "txt"])
job_description = st.text_input("Enter the job role description(optional)")

analyze = st.button("Analyze Resume")

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(uploaded_file.read()))
    return uploaded_file.read().decode("utf-8")

def generate_pdf_report(analysis_text):

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    

    clean_text = re.sub(r'<[^>]*>', '', analysis_text)

    clean_text = clean_text.replace("&", "and")

    content = [

        Paragraph("CVForge AI Resume Analysis Report", styles["Title"]),

        Spacer(1, 12)

    ]

    

    for line in clean_text.split("\n"):

        line = line.strip()

        if line:

            content.append(

                Paragraph(line, styles["BodyText"])

            )

            content.append(Spacer(1, 4))

    doc.build(content)

    buffer.seek(0)

    return buffer


if analyze and upload_file:
    try:
        file_content = extract_text_from_file(upload_file)
        if not file_content.strip():
            st.error("File does not have any content...")
            st.stop()

        prompt = f"""Please analyze this resume and provide constructive feedback.
        MostIMPORTANT notes before generating the response:
- Do NOT use HTML tags anywhere in the response.
- Do NOT use <br>, <p>, <ul>, or any HTML formatting anywhere in the response.
- Return plain Markdown only.
Focus on the following aspects:
1. Content clarity and impact
2. Skills presentation
3. Experience descriptions
4. ATS Score: <score out of 100>
5. Strengths:
- Point 1
- Point 2
- Point 3

6. Weaknesses:
- Point 1
- Point 2
- Point 3

7. Missing Keywords:
- Keyword 1
- Keyword 2
- Keyword 3

8. Recommendations:
- Recommendation 1
- Recommendation 2
- Recommendation 3

9. Also provide job matching score out of 100 based on the job description provided. If no job description is provided, provide a general score based on the resume content.

10. Specific improvements for job_description if job_description else 'general job applications'

Job Description:
{job_description if job_description else "General"}

Resume:
{file_content}

Please provide your analysis in a clear, structured format with specific recommendations.
"""
        
        client = OpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1"
        )
        with st.spinner("🔍 Analyzing your resume..."):
            response = client.chat.completions.create(
                model="openai/gpt-oss-20b:free",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert resume reviewer with years of experience in HR and recruitment."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1000
            )

            st.success("🎉 Resume analysis completed successfully!")
            st.balloons()

        analysis = response.choices[0].message.content

        st.markdown("### Analysis Results")
        st.markdown(analysis)

        pdf_file = generate_pdf_report(analysis)

        st.download_button(
            label="📥 Download PDF Report",
            data=pdf_file,
            file_name="CVForge_AI_Report.pdf",
            mime="application/pdf"
        )

    except Exception as e:
        st.error("Something went wrong while generating the report.")
        print(e)

