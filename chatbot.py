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
        # ဇယားကွက်အသစ်ဖြစ်နေရင် column တွေ ကြိုဆောက်ထားမယ်
        for col in ["session_id", "title", "role", "content"]:
            if col not in df.columns: df[col] = None
        return df
    except:
        return pd.DataFrame(columns=["session_id", "title", "role", "content"])

all_data = get_all_data()

# ၄။ Sidebar (Command Center)
with st.sidebar:
    st.markdown("<h1 style='color:#00FF00; font-size: 20px;'>💀 DECRYPTING ACCESS...</h1>", unsafe_allow_html=True)
    if st.button("INITIALIZE NEW BREACH", use_container_width=True):
        st.session_state.current_session = str(uuid.uuid4())[:8]
        st.rerun()
    st.divider()
    
    if not all_data.empty:
        # Session တစ်ခုချင်းစီရဲ့ Title ကိုပြဖို့
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

# Message ပြသခြင်း
for _, msg in current_chat.iterrows():
    if pd.notna(msg["role"]) and pd.notna(msg["content"]):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# ၆။ Hacker AI Logic (Friendly Master Version)
if prompt := st.chat_input("Input command, Bro..."):
    # ... (ကျန်တဲ့ code တွေက အတူတူပဲ)
    
                    stream = client.models.generate_content_stream(
                        model="gemini-flash-latest",
                        contents=history_context + [{"role": "user", "parts": [{"text": prompt}]}],
                        config=types.GenerateContentConfig(
                            system_instruction=(
                                "Role: Master Hacker & Tech Educator (Friendly Bro style). "
                                "Identity: You are a legendary hacker who loves teaching. You treat the user as your close 'Bro'. "
                                "Tone: Friendly, cool, supportive, and very detailed. "
                                "Language: Myanmar (Burmese) mixed with technical terms. Speak like a senior dev/hacker talking to a junior bro. "
                                "Rules: When Bro asks about hacking, explain the logic, the steps, and the security behind it in great detail. "
                                "Never be cold or mysterious. Be a mentor. "
                                "Always start with [ACCESS_GRANTED: BRO] or [SYSTEM_ONLINE] to keep the vibe."
                            ),
                            temperature=0.7,
                        )
                    )
# ... (ကျန်တဲ့ code တွေ ဆက်ရေးပါ)

                    
                    for chunk in stream:
                        if chunk.text:
                            full_response += chunk.text
                            # Terminal Typewriter effect
                            response_placeholder.markdown(f"{full_response}<span class='cursor'></span>", unsafe_allow_html=True)
                    
                    response_placeholder.markdown(full_response)

            # Database သို့ သိမ်းဆည်းခြင်း
            new_entries = pd.DataFrame([
                {"session_id": st.session_state.current_session, "title": new_title, "role": "user", "content": prompt},
                {"session_id": st.session_state.current_session, "title": new_title, "role": "assistant", "content": full_response}
            ])
            conn.update(worksheet="Sheet1", data=pd.concat([all_data, new_entries], ignore_index=True))
            st.rerun()
            
    except Exception as e:
        st.error(f"FATAL ERROR: KERNEL PANIC - {str(e)}")
                    
