import streamlit as st
from google import genai
import io

# API Config
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
except:
    st.error("API Key config Error!")

# UI Design (Hacker Dark Theme)
st.set_page_config(page_title="Cyber Bot MM", page_icon="🛡️", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #00ff41; }
    .stButton>button { background-color: #6200ea; color: white; border-radius: 8px; border: none; }
    .stChatInput { border: 1px solid #00ff41; }
    </style>
    """, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("⚙️ Hacker's Menu")
    mode = st.selectbox("Role Selection", ["Hacking Specialist", "Code Analyzer", "Linux Expert"])
    uploaded_file = st.file_uploader("Upload Code/Logs", type=['py','js','txt','php','html'])
    if st.button("🗑️ Clear History"):
        st.session_state.messages = []
        st.rerun()

# Chat System
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask about Hacking/Coding..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        file_content = ""
        if uploaded_file:
            file_content = f"\n[FILE DATA]:\n{uploaded_file.getvalue().decode()}"
        
        try:
            full_prompt = f"System: {mode} (Answer in Myanmar). {file_content}\nUser: {prompt}"
            response = client.models.generate_content(model="gemini-1.5-flash", contents=full_prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Error: {e}")
