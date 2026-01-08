import streamlit as st
import random
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from google import genai
from google.genai import types
import uuid
import time

# ၁။ UI Configuration
st.set_page_config(page_title="HACKER TERMINAL V2", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #000000; color: #00FF00; font-family: 'Courier New', Courier, monospace; }
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageUser"]) {
        flex-direction: row-reverse !important;
        text-align: right !important;
        background-color: #1a1a1a !important;
        border-right: 3px solid #333333 !important;
    }
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAssistant"]) {
        background-color: #0a0a0a !important;
        border-left: 3px solid #00FF00 !important;
    }
    .stButton>button { border-radius: 5px; border: 1px solid #00FF00; background: black; color: #00FF00; }
    </style>
    """, unsafe_allow_html=True)

# ၂။ Connection & API Keys
conn = st.connection("gsheets", type=GSheetsConnection)
KEYS = [
    st.secrets.get("KEY1"), st.secrets.get("KEY2"), 
    st.secrets.get("KEY3"), st.secrets.get("KEY4"), 
    st.secrets.get("KEY5")
]

def get_ai_client():
    valid_keys = [k for k in KEYS if k]
    if not valid_keys: return None
    return genai.Client(api_key=random.choice(valid_keys))

# ၃။ Session Logic
if "current_session" not in st.session_state:
    st.session_state.current_session = str(uuid.uuid4())[:8]

def get_all_data():
    try:
        df = conn.read(worksheet="Sheet1", ttl=0)
        for col in ["session_id", "title", "role", "content"]:
            if col not in df.columns: df[col] = None
        return df
    except:
        return pd.DataFrame(columns=["session_id", "title", "role", "content"])

all_data = get_all_data()

# ၄။ Sidebar
with st.sidebar:
    st.title("💀 COMMAND CENTER")
    if st.button("EXECUTE NEW SESSION", use_container_width=True):
        st.session_state.current_session = str(uuid.uuid4())[:8]
        st.rerun()
    st.divider()
    if not all_data.empty:
        session_list = all_data.dropna(subset=['session_id']).drop_duplicates('session_id', keep='first')
        for _, row in session_list.iloc[::-1].iterrows():
            col1, col2 = st.columns([4, 1])
            with col1:
                if st.button(f"🔗 {row['title']}", key=f"s_{row['session_id']}", use_container_width=True):
                    st.session_state.current_session = row['session_id']
                    st.rerun()
            with col2:
                if st.button("❌", key=f"d_{row['session_id']}"):
                    all_data = all_data[all_data["session_id"] != row['session_id']]
                    conn.update(worksheet="Sheet1", data=all_data)
                    st.rerun()

# ၅။ Main Display
current_chat = all_data[all_data["session_id"] == st.session_state.current_session]
current_title = current_chat['title'].iloc[0] if not current_chat.empty else "Ready to Infiltrate"
st.markdown(f"#### > TARGET: `{current_title}`")

for _, msg in current_chat.iterrows():
    if pd.notna(msg["role"]) and pd.notna(msg["content"]):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# ၆။ AI Logic (အမှားပြင်ဆင်ပြီး ဗားရှင်း)
if prompt := st.chat_input("Input command, Bro..."):
    new_title = prompt[:20] if current_chat.empty else current_title
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        client = get_ai_client()
        if client:
            history_context = []
            for _, row in current_chat.iterrows():
                role_label = "user" if row["role"] == "user" else "model"
                history_context.append({"role": role_label, "parts": [{"text": row["content"]}]})
            
                        with st.chat_message("assistant"):
                # ၁။ AI စဉ်းစားနေစဉ် အဝိုင်းလည်ပြမယ်
                with st.spinner("INFILTRATING NETWORK..."):
                    # အမှားပြင်ဆင်ချက်- generate_content နေရာတွင် generate_content_stream ကို သုံးပါ
                    stream = client.models.generate_content_stream(
                        model="gemini-1.5-flash",
                        contents=history_context + [{"role": "user", "parts": [{"text": prompt}]}],
                        config=types.GenerateContentConfig(
                            system_instruction=(
                                "You are a notorious Blackhat Hacker and Cyber Security Expert. "
                                "Your tone is dark, mysterious, cold but helpful to your peer (Bro) in Myanmar language. "
                                "Use hacker terminologies. You are a digital entity. "
                                "Be technical and sharp."
                            ),
                            temperature=0.7,
                        )
                    )
                    
                    response_placeholder = st.empty()
                    full_response = ""
                    
                    # stream function ဖြစ်တဲ့အတွက် chunk တွေကို loop ပတ်လို့ရပါပြီ
                    for chunk in stream:
                        if chunk.text:
                            full_response += chunk.text
                            response_placeholder.markdown(full_response + " █")
                    
                    response_placeholder.markdown(full_response)
                    
                    
                    # ၄။ နောက်ဆုံးမှာ Cursor ကို ဖျောက်မယ်
                    response_placeholder.markdown(full_response)

            # Save to GSheets
            new_entries = pd.DataFrame([
                {"session_id": st.session_state.current_session, "title": new_title, "role": "user", "content": prompt},
                {"session_id": st.session_state.current_session, "title": new_title, "role": "assistant", "content": full_response}
            ])
            conn.update(worksheet="Sheet1", data=pd.concat([all_data, new_entries], ignore_index=True))
            st.rerun()
            
    except Exception as e:
        st.error(f"ENCRYPTION FAILURE: {str(e)}")
            
