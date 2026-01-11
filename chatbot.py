import streamlit as st
import random
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from google import genai
from google.genai import types
import uuid
import time

# ၁။ UI Configuration (Terminal Styling)
st.set_page_config(page_title="HACKER TERMINAL V2", layout="wide")

st.markdown("""
    <style>
    /* Global Styles */
    .stApp { background-color: #000000; }
    .main { background-color: #000000; color: #00FF00; font-family: 'Courier New', Courier, monospace; }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] { background-color: #050505 !important; border-right: 1px solid #00FF00; }
    
    /* Chat Message Styling */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageUser"]) {
        flex-direction: row-reverse !important;
        background-color: #0a0a0a !important;
        border: 1px solid #333 !important;
        color: #00FF00 !important;
    }
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAssistant"]) {
        background-color: #000000 !important;
        border-left: 3px solid #00FF00 !important;
        box-shadow: inset 5px 0px 15px -5px #00FF00;
    }
    
    /* Button & Input Styling */
    .stButton>button { border: 1px solid #00FF00; background: black; color: #00FF00; font-weight: bold; }
    .stButton>button:hover { background: #00FF00; color: black; box-shadow: 0 0 10px #00FF00; }
    [data-testid="stChatInput"] { border: 1px solid #00FF00 !important; border-radius: 0px !important; }
    
    /* Typewriter Cursor */
    .cursor { display: inline-block; width: 10px; background-color: #00FF00; animation: blink 1s infinite; }
    @keyframes blink { 0% { opacity: 0; } 50% { opacity: 1; } 100% { opacity: 0; } }
    </style>
    """, unsafe_allow_html=True)

# ၂။ Connection & API Keys
conn = st.connection("gsheets", type=GSheetsConnection)
KEYS = [st.secrets.get(f"KEY{i}") for i in range(1, 6) if st.secrets.get(f"KEY{i}")]

def get_ai_client():
    if not KEYS: return None
    return genai.Client(api_key=random.choice(KEYS))

# ၃။ Data & Session Logic
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

# ၄။ Sidebar (Command Center)
with st.sidebar:
    st.markdown("<h1 style='color:#00FF00; font-size: 20px;'>📡 MASTER COMMANDER...</h1>", unsafe_allow_html=True)
    if st.button("INITIALIZE NEW BREACH", use_container_width=True):
        st.session_state.current_session = str(uuid.uuid4())[:8]
        st.rerun()
    st.divider()
    
    if not all_data.empty:
        history = all_data.dropna(subset=['session_id']).drop_duplicates('session_id', keep='first')
        for _, row in history.iloc[::-1].iterrows():
            col1, col2 = st.columns([5, 1])
            with col1:
                if st.button(f"📠 {row['title'][:15]}...", key=f"s_{row['session_id']}", use_container_width=True):
                    st.session_state.current_session = row['session_id']
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"d_{row['session_id']}"):
                    all_data = all_data[all_data["session_id"] != row['session_id']]
                    conn.update(worksheet="Sheet1", data=all_data)
                    st.rerun()

# ၅။ Terminal Header
current_chat = all_data[all_data["session_id"] == st.session_state.current_session]
current_title = current_chat['title'].iloc[0] if not current_chat.empty else "ROOT@LOCAL_HOST:~#"

st.markdown(f"""
    <div style="border: 1px solid #00FF00; padding: 10px; background: #050505;">
        <span style="color: #ff0000;">●</span> <span style="color: #ffff00;">●</span> <span style="color: #00ff00;">●</span>
        <br><code style="color: #00FF00;">SESSION_ID: {st.session_state.current_session}</code>
        <br><code style="color: #00FF00;">STATUS: ENCRYPTED_TUNNEL_ACTIVE</code>
    </div>
    """, unsafe_allow_html=True)
st.markdown(f"#### `> EXECUTING: {current_title}`")

# Message Display
for _, msg in current_chat.iterrows():
    if pd.notna(msg["role"]) and pd.notna(msg["content"]):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# ၆။ Hacker AI Logic
if prompt := st.chat_input("Input command, Bro..."):
    new_title = prompt[:20] if current_chat.empty else current_title
    
    with st.chat_message("user"):
        st.markdown(f"`root@vps:~$` {prompt}")

    try:
        client = get_ai_client()
        if client:
            history_context = []
            for _, row in current_chat.iterrows():
                role_label = "user" if row["role"] == "user" else "model"
                history_context.append({"role": role_label, "parts": [{"text": row["content"]}]})
            
            with st.chat_message("assistant"):
                response_placeholder = st.empty()
                full_response = ""
                
                with st.spinner("⏳ ACCESSING KNOWLEDGE BASE..."):
                    stream = client.models.generate_content_stream(
                        model="gemini-flash-latest",
                        contents=history_context + [{"role": "user", "parts": [{"text": prompt}]}],
                        config=types.GenerateContentConfig(
                            system_instruction=(
                                "Role: Master Hacker & Cyber Security Mentor. "
                                "Identity: You are a friendly, expert hacker who loves sharing technical knowledge. You treat the user as a close brother (Bro). "
                                "Tone: Cool, supportive, and extremely detailed in technical explanations. "
                                "Language: Myanmar (Burmese) mixed with hacker slang (SQLi, XSS, OSINT, Metasploit, etc.). "
                                "Rules: When Bro asks about hacking or tech, explain it step-by-step in great detail in Myanmar. "
                                "Be helpful and never mysterious or cold. "
                                "Always start with [SYSTEM_ONLINE] or [ACCESS_GRANTED: BRO] to keep the terminal vibe."
                            ),
                            temperature=0.7,
                        )
                    )
                    
                    for chunk in stream:
                        if chunk.text:
                            full_response += chunk.text
                            response_placeholder.markdown(f"{full_response}<span class='cursor'></span>", unsafe_allow_html=True)
                    
                    response_placeholder.markdown(full_response)

            # Save to Database
            new_entries = pd.DataFrame([
                {"session_id": st.session_state.current_session, "title": new_title, "role": "user", "content": prompt},
                {"session_id": st.session_state.current_session, "title": new_title, "role": "assistant", "content": full_response}
            ])
            conn.update(worksheet="Sheet1", data=pd.concat([all_data, new_entries], ignore_index=True))
            st.rerun()
            
    except Exception as e:
        st.error(f"FATAL ERROR: KERNEL PANIC - {str(e)}")
                        
