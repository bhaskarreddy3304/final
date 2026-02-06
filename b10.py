# ==========================================
# LEGAL AI – ChatGPT Style (FINAL + ALERT)
# ==========================================

import streamlit as st
import speech_recognition as sr
import pyttsx3
import threading
import io
import time

from pypdf import PdfReader
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.llms import HuggingFacePipeline
from langchain.embeddings.base import Embeddings

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from sentence_transformers import SentenceTransformer

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Legal AI",
    page_icon="⚖️",
    layout="wide"
)

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
if "chat" not in st.session_state:
    st.session_state.chat = []

if "speaking" not in st.session_state:
    st.session_state.speaking = False

if "question_text" not in st.session_state:
    st.session_state.question_text = ""

# --------------------------------------------------
# THEME
# --------------------------------------------------
theme = st.sidebar.radio("🌗 Theme", ["Light", "Dark"])

if theme == "Light":
    BG, CARD, TEXT, BORDER, INPUT = "#f7f7f8", "#ffffff", "#0f172a", "#e5e7eb", "#ffffff"
else:
    BG, CARD, TEXT, BORDER, INPUT = "#020617", "#0f172a", "#e5e7eb", "#1f2937", "#020617"

ACCENT = "#10a37f"

# --------------------------------------------------
# CSS
# --------------------------------------------------
st.markdown(f"""
<style>
.stApp {{ background:{BG}; color:{TEXT}; }}
.card {{
    background:{CARD};
    border:1px solid {BORDER};
    border-radius:16px;
    padding:20px;
    margin-top:20px;
}}
.answer {{
    background:{INPUT};
    border-left:4px solid {ACCENT};
    padding:16px;
    border-radius:10px;
    line-height:1.6;
}}
button {{
    background:{ACCENT}!important;
    color:white!important;
    border-radius:10px!important;
    font-weight:600!important;
}}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.markdown("<h1 style='text-align:center;'>⚖️ Legal Document Analysis and Q&A using RAG Framework</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Voice-Enabled Legal Assistant using RAG</p>", unsafe_allow_html=True)

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
st.sidebar.markdown("## 📂 Upload Legal PDFs")
files = st.sidebar.file_uploader(
    "Upload documents",
    type=["pdf"],
    accept_multiple_files=True
)

st.sidebar.markdown("---")
st.sidebar.markdown("## 🧠 System Capabilities")
st.sidebar.markdown("""
✅ Legal PDF Analysis  
✅ Contract & Case Q&A  
✅ 🎤 Voice Input  
✅ 🔊 Read Answer  
✅ ⏹ Stop Reading  
✅ 📄 Download PDF  
""")

# --------------------------------------------------
# EMBEDDINGS
# --------------------------------------------------
class HFEmbeddings(Embeddings):
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def embed_documents(self, texts):
        return self.model.encode(texts).tolist()

    def embed_query(self, text):
        return self.model.encode([text])[0].tolist()

# --------------------------------------------------
# BUILD RAG
# --------------------------------------------------
@st.cache_resource
def build_rag(chunks, meta):
    db = FAISS.from_texts(chunks, HFEmbeddings(), meta)

    tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-base")
    model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-base")

    pipe = pipeline(
        "text2text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=300
    )

    return RetrievalQA.from_chain_type(
        llm=HuggingFacePipeline(pipeline=pipe),
        retriever=db.as_retriever()
    )

# --------------------------------------------------
# VOICE INPUT
# --------------------------------------------------
def voice_input():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
    try:
        return r.recognize_google(audio)
    except:
        return ""

# --------------------------------------------------
# SPEAK / STOP WITH ALERT CONTROL
# --------------------------------------------------
def speak_answer(text):
    engine = pyttsx3.init()
    engine.setProperty("rate", 165)

    st.session_state.speaking = True
    engine.say(text)
    engine.runAndWait()

    st.session_state.speaking = False
    time.sleep(0.2)  # allow UI refresh
    st.rerun()

def stop_speaking():
    try:
        pyttsx3.init().stop()
    except:
        pass
    st.session_state.speaking = False
    st.rerun()

# --------------------------------------------------
# PDF GENERATION
# --------------------------------------------------
def generate_pdf(question, answer):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)

    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("<b>LEGAL AI REPORT</b>", styles["Title"]))
    story.append(Paragraph("<br/><b>Question:</b>", styles["Heading2"]))
    story.append(Paragraph(question, styles["Normal"]))
    story.append(Paragraph("<br/><b>Answer:</b>", styles["Heading2"]))
    story.append(Paragraph(answer, styles["Normal"]))

    doc.build(story)
    buffer.seek(0)
    return buffer

# --------------------------------------------------
# MAIN APP
# --------------------------------------------------
if files:
    texts, metas = [], []

    for f in files:
        reader = PdfReader(f)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                texts.append(text)
                metas.append({"source": f.name})

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)

    chunks, meta = [], []
    for t, m in zip(texts, metas):
        for c in splitter.split_text(t):
            chunks.append(c)
            meta.append(m)

    qa = build_rag(chunks, meta)

    col1, col2 = st.columns([6, 1])

    with col1:
        st.session_state.question_text = st.text_input(
            "Ask a legal question…",
            value=st.session_state.question_text
        )

    with col2:
        if st.button("🎤"):
            spoken = voice_input()
            if spoken:
                st.session_state.question_text = spoken
                st.rerun()

    if st.session_state.question_text:
        with st.spinner("Analyzing documents…"):
            answer = qa(st.session_state.question_text)["result"]

        st.session_state.chat.append((st.session_state.question_text, answer))
        st.session_state.question_text = ""

    # 🔔 ALERT BOX WHILE SPEAKING
    if st.session_state.speaking:
        st.warning("🔊 Reading answer… Please wait")

    if st.session_state.chat:
        q, a = st.session_state.chat[-1]

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown(f"**Question:** {q}")
        st.markdown(f"<div class='answer'>{a}</div>", unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)

        with c1:
            if st.button("🔊 Read Answer"):
                if not st.session_state.speaking:
                    threading.Thread(
                        target=speak_answer,
                        args=(a,),
                        daemon=True
                    ).start()

        with c2:
            if st.button("⏹ Stop Reading"):
                stop_speaking()

        with c3:
            pdf = generate_pdf(q, a)
            st.download_button(
                "📄 Download PDF",
                data=pdf,
                file_name="Legal_AI_Report.pdf",
                mime="application/pdf"
            )

        st.markdown("</div>", unsafe_allow_html=True)

else:
    st.info("📂 Upload legal PDF documents to begin.")
