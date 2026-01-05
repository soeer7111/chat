import streamlit as st
import random
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from google import genai
from google.genai import types
import uuid
import time

# ၁။ UI Configuration (Dark Theme)
st.set_page_config(page_title="CYBER ASSISTANT TERMINAL", layout="wide")

# CSS နဲ့ UI ကို ပိုကောင်းအောင် ပြင်ဆင်ခြင်း
st.markdown("""
    <style>
    .main { background-color: #000000; color: #e0e0e0; }
    /* Message တွေကို ဘယ်ညာခွဲရန် */
    [data-testid="stChatMessage"] { border-radius: 15px; margin-bottom: 10px; }
    /* User Message (ညာဘက်) */
    [data-testid="stChatMessage"]:nth-child(even) {
        flex-direction: row-reverse;
        background-color: #1e1e1e;
        text-align: right;
    }
    /* Assistant Message (ဘယ်ဘက်) */
    [data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #0d0d0d;
        border-left: 3px solid #00FF00;
    }
    .stButton>button { border-radius: 20px; }
    </style>
    """, unsafe_allow_html=True)

# ၂။ Connection & API Keys (မပြင်ထားပါ)
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

# ၄။ Sidebar (History & Delete Feature)
with st.sidebar:
    st.title("📟 OPERATION LOGS")
    if st.button("➕ NEW SESSION", use_container_width=True):
        st.session_state.current_session = str(uuid.uuid4())[:8]
        st.rerun()
    
    st.divider()
    
    if not all_data.empty:
        session_list = all_data[['session_id', 'title']].drop_duplicates('session_id', keep='first')
        for _, row in session_list.iloc[::-1].iterrows():
            col1, col2 = st.columns([4, 1])
            with col1:
                if st.button(f"📁 {row['title']}", key=row['session_id'], use_container_width=True):
                    st.session_state.current_session = row['session_id']
                    st.rerun()
            with col2:
                # Delete Button (Hold effect simulation using context menu or simple confirm)
                if st.button("🗑️", key=f"del_{row['session_id']}"):
                    # ၂ စက္ကန့် စောင့်ခိုင်းတာထက် ပိုမြန်အောင် Confirmation လုပ်ပေးထားပါတယ်
                    with st.spinner("Deleting..."):
                        time.sleep(1) # Simulation delay
                        all_data = all_data[all_data["session_id"] != row['session_id']]
                        conn.update(worksheet="Sheet1", data=all_data)
                        st.rerun()

# ၅။ Main Display
current_chat = all_data[all_data["session_id"] == st.session_state.current_session]
current_title = current_chat['title'].iloc[0] if not current_chat.empty else "New Sequence"

st.markdown(f"#### > CURRENT SESSION: {current_title}")

for _, msg in current_chat.iterrows():
    if pd.notna(msg["role"]) and pd.notna(msg["content"]):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# ၆။ AI Logic with Spinner
if prompt := st.chat_input("Ask anything, Bro..."):
    if current_chat.empty:
        new_title = prompt[:20] + "..." if len(prompt) > 20 else prompt
    else:
        new_title = current_title

    user_entry = pd.DataFrame([{
        "session_id": st.session_state.current_session,
        "title": new_title, "role": "user", "content": prompt
    }])
    
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        client = get_ai_client()
        if client:
            # Spinner (အဝိုင်းလည်နေမည့်ပုံစံ)
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = client.models.generate_content(
                        model="gemini-flash-latest",
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            system_instruction=(
                                "You are Gemini, a helpful and smart Cyber Security Expert. "
                                "Respond like a helpful peer (Bro) in Myanmar language. "
                                "Provide clear, technical, and actionable advice. "
                                "Be empathetic and insightful like a mentor."
                            ),
                            temperature=0.9,
                        )
                    )
                    ai_res = response.text
                    st.markdown(ai_res)
            
            ai_entry = pd.DataFrame([{
                "session_id": st.session_state.current_session,
                "title": new_title, "role": "assistant", "content": ai_res
            }])
            
            final_df = pd.concat([all_data, user_entry, ai_entry], ignore_index=True)
            conn.update(worksheet="Sheet1", data=final_df)
            st.rerun()
            
    except Exception as e:
        st.error(f"SYSTEM FAILURE: {str(e)}")
                                
