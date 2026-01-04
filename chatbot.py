import streamlit as st
from google import genai
from google.genai import types

# ၁။ API Configuration
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Secrets ထဲမှာ GEMINI_API_KEY ထည့်ပေးပါဦး Bro!")
    st.stop()

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# ၂။ UI/UX Design (Mobile Friendly & Hacker Style)
st.set_page_config(page_title="Hacker Bot Pro", layout="centered")

st.markdown("""
    <style>
    /* Background & Layout */
    .stApp { background-color: #000000; color: #00ff41; font-family: monospace; }
    
    /* Message Alignment (ဘယ်/ညာ ခွဲခြင်း) */
    .stChatMessage { margin-bottom: 12px; border-radius: 15px; border: none !important; }

    /* User Message (ညာဘက် - Right) */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarUser"]) {
        flex-direction: row-reverse;
        background-color: #003311 !important;
        margin-left: 20% !important;
    }

    /* Assistant Message (ဘယ်ဘက် - Left) */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarAssistant"]) {
        background-color: #111111 !important;
        margin-right: 20% !important;
        border: 0.5px solid #00ff4133 !important;
    }

    /* Chat Input Box (အမြဲအောက်မှာရှိနေစေရန် Streamlit က လုပ်ပေးထားပါတယ်) */
    div[data-testid="stChatInput"] { border: 1px solid #00ff41 !important; }
    </style>
    """, unsafe_allow_html=True)

# ၃။ Chat History Persistence (Reload လုပ်ရင် စာမပျောက်အောင်)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    st.title("🥷 TERMINAL")
    st.write("Code editor")
    if st.button("RESET CHAT"):
        st.session_state.messages = []
        st.rerun()

# ၄။ စာဟောင်းများကို ပြသခြင်း (အသစ်ပို့ရင် အလိုအလျောက် အောက်မှာပဲ ပေါ်နေမှာပါ)
# container ကို သုံးပြီး message အသစ်ကို အမြဲ အောက်မှာ ပေါ်အောင် လုပ်ထားပါတယ်
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ၅။ Chat Input Logic
if prompt := st.chat_input("Command..."):
    # User message ကို သိမ်းမယ်
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI Response
    with st.chat_message("assistant"):
        try:
            config = types.GenerateContentConfig(
                system_instruction="You are a Cybersecurity Expert. Answer in Myanmar language.",
                safety_settings=[{"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}],
                temperature=0.8
            )
            
            response = client.models.generate_content(
                model="gemini-flash-latest", 
                contents=prompt,
                config=config
            )
            
            res_text = response.text
            st.markdown(res_text)
            # AI အဖြေကို သိမ်းမယ် (ဒါကြောင့် Reload လုပ်လည်း မပျောက်တာပါ)
            st.session_state.messages.append({"role": "assistant", "content": res_text})
            
        except Exception as e:
            if "429" in str(e):
                st.warning("⚠️ Terminal Limit: အခုချိန်မှာ လူသုံးများနေလို့ (သို့မဟုတ်) limit ပြည့်သွားလို့ပါ။ ၁ မိနစ်လောက်စောင့်ပြီးမှ ပြန်မေးပေးပါ Bro။")
            else:
                st.error("⚠️ Connection Error: ခဏနေမှ ပြန်စမ်းကြည့်ပါဦး။")
                
