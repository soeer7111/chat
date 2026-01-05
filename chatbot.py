import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from google import genai
from google.genai import types
import uuid
import random # API Key များကို random ရွေးရန် ထည့်ပေးထားသည်

# ၁။ UI & Connection
st.set_page_config(page_title="Hacker AI Pro", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

# ၂။ Session Management
if "current_session" not in st.session_state:
    st.session_state.current_session = str(uuid.uuid4())[:8]

# ၃။ Gemini API Client Setup (API Key ၅ ခု Rotation Logic)
KEYS = [
    st.secrets.get("KEY1"), 
    st.secrets.get("KEY2"), 
    st.secrets.get("KEY3"),
    st.secrets.get("KEY4"),
    st.secrets.get("KEY5")
]

def get_ai_client():
    valid_keys = [k for k in KEYS if k]
    if not valid_keys:
        return None
    # Key ၅ ခုထဲမှ တစ်ခုကို random ရွေးသုံးပေးမည်
    return genai.Client(api_key=random.choice(valid_keys))

# ၄။ Sheet ထဲက Data အားလုံးဖတ်ခြင်း
def get_all_data():
    try:
        return conn.read(worksheet="Sheet1", ttl=0)
    except:
        return pd.DataFrame(columns=["session_id", "title", "role", "content"])

all_data = get_all_data()

# ၅။ Sidebar: Chat History with Names
with st.sidebar:
    st.title("🥷 CHAT HISTORY")
    if st.button("➕ New Chat"):
        st.session_state.current_session = str(uuid.uuid4())[:8]
        st.rerun()
    
    st.divider()
    
    if not all_data.empty:
        # Session ID တစ်ခုချင်းစီရဲ့ ပထမဆုံး Title ကို ယူမယ်
        session_list = all_data[['session_id', 'title']].drop_duplicates('session_id', keep='first')
        for _, row in session_list.iloc[::-1].iterrows():
            # ခေါင်းစဉ်နာမည်လေးတွေနဲ့ ခလုတ်လုပ်မယ်
            if st.button(f"📁 {row['title']}", key=row['session_id'], use_container_width=True):
                st.session_state.current_session = row['session_id']
                st.rerun()

# ၆။ Main Chat Area
current_chat = all_data[all_data["session_id"] == st.session_state.current_session]
# လက်ရှိ Session ရဲ့ Title ကို ရှာခြင်း
current_title = current_chat['title'].iloc[0] if not current_chat.empty else "New Chat"
st.subheader(f"Topic: {current_title}")

for _, msg in current_chat.iterrows():
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ၇။ Input Logic
if prompt := st.chat_input("Ask me anything..."):
    # ပထမဆုံးစာဆိုရင် အဲ့ဒီစာကိုပဲ Title အဖြစ် သတ်မှတ်မယ်
    if current_chat.empty:
        new_title = prompt[:20] + "..." if len(prompt) > 20 else prompt
    else:
        new_title = current_title

    # User Message သိမ်းခြင်း
    user_entry = pd.DataFrame([{
        "session_id": st.session_state.current_session,
        "title": new_title,
        "role": "user",
        "content": prompt
    }])
    
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI Response
    try:
        client = get_ai_client()
        if client:
            response = client.models.generate_content(model="gemini-flash-latest", contents=prompt)
            ai_res = response.text
            
            with st.chat_message("assistant"):
                st.markdown(ai_res)
            
            # AI Message သိမ်းခြင်း
            ai_entry = pd.DataFrame([{
                "session_id": st.session_state.current_session,
                "title": new_title,
                "role": "assistant",
                "content": ai_res
            }])
            
            final_df = pd.concat([all_data, user_entry, ai_entry], ignore_index=True)
            conn.update(worksheet="Sheet1", data=final_df)
            st.rerun()
        else:
            st.error("API Keys missing in secrets.")
        
    except Exception as e:
        st.error(f"Error: {str(e)}")
            
