import streamlit as st
from google import genai

# ၁။ API Configuration
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
except Exception as e:
    st.error(f"API Key Error: {e}")

st.set_page_config(page_title="Gemini 3 Hacker AI", page_icon="⚡")

# Gemini 3 အတွက် Model ID အမှန်
# ရှေ့က models/ မပါရပါဘူး
MODEL_ID = "gemini-3-flash-preview"

st.title("⚡ Gemini 3 Hacker Chatbot")
st.caption("Next-Gen Experimental AI for Hacking & Coding")

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
            # Gemini 3 ကို System Instruction နဲ့ ခေါ်မယ်
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=f"You are a Cybersecurity and Programming Expert. Help the user in Myanmar language: {prompt}"
            )
            
            answer = response.text
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            
        except Exception as e:
            # Error တက်ရင် ဘာကြောင့်လဲဆိုတာ အတိအကျပြမယ်
            st.error(f"Error Type: {type(e).__name__}")
            st.error(f"Message: {e}")
            
