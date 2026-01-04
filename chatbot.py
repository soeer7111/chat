import streamlit as st
from google import genai
import io
from PIL import Image

# ၁။ API Configuration
try:
    # Streamlit Cloud ရဲ့ Secrets ထဲမှာ GEMINI_API_KEY ရှိရပါမယ်
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
except Exception as e:
    st.error(f"API Key config Error: {e}")

st.set_page_config(page_title="Hacker Bot MM", page_icon="🛡️", layout="wide")

# Hacker Style Dark Theme
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #00ff41; }
    .stChatInput { border: 1px solid #00ff41 !important; }
    .stButton>button { background-color: #1a1c23; color: #00ff41; border: 1px solid #00ff41; }
    </style>
    """, unsafe_allow_html=True)

# Model ID ကို အရှေ့က models/ မပါဘဲ ဒီလိုပဲ ရေးပါ
MODEL_ID = "gemini-1.5-flash" 

with st.sidebar:
    st.title("🛡️ Hacker Setup")
    mode = st.selectbox("Select Role", ["General Hacker", "Code Reviewer", "CTF Solver"])
    uploaded_file = st.file_uploader("Upload Code File", type=['py', 'js', 'php', 'txt'])
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Hacking သို့မဟုတ် Programming အကြောင်း မေးမြန်းပါ..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # File ပါလာရင် content ထဲ ထည့်ဖတ်မယ်
            context = ""
            if uploaded_file:
                context = f"\n[FILE ATTACHED]:\n{uploaded_file.getvalue().decode('utf-8')}\n"

            # API Call (MODEL_ID က အခု "gemini-1.5-flash" ပဲ ဖြစ်ရပါမယ်)
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=f"System: You are a {mode} answering in Myanmar. {context}\nUser: {prompt}"
            )
            
            res_text = response.text
            st.markdown(res_text)
            st.session_state.messages.append({"role": "assistant", "content": res_text})
            
        except Exception as e:
            # Error Message ကို သေချာပြပေးမယ်
            st.error(f"AI Error: {e}")
