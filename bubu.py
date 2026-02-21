import streamlit as st
import google.generativeai as genai
import openai  # DeepSeek ke liye (OpenAI compatible API)
import random

# Page config
st.set_page_config(
    page_title="Bubu AI",
    page_icon="🤖",
    layout="wide"
)

# CSS for styling
st.markdown("""
<style>
    .stTextInput {
        position: fixed;
        bottom: 20px;
        width: 70%;
        z-index: 999;
    }
    .user-message {
        background-color: #007AFF;
        color: white;
        padding: 10px 15px;
        border-radius: 20px 20px 5px 20px;
        max-width: 70%;
        margin: 5px 0;
        margin-left: auto;
    }
    .assistant-message {
        background-color: #E9ECEF;
        color: black;
        padding: 10px 15px;
        border-radius: 20px 20px 20px 5px;
        max-width: 70%;
        margin: 5px 0;
    }
    .chat-container {
        padding: 20px;
        margin-bottom: 80px;
    }
</style>
""", unsafe_allow_html=True)

# ---------- API KEYS (TERI KEYS DAL) ----------
GEMINI_KEY = "AIzaSyDWJDDu-3utug2GJmPwFwT_5kZHXPeR6YU"  # Teri Gemini key
DEEPSEEK_KEY = "sk-5c6d20af09ea4deeb37c09207c677397"  # Yahan DeepSeek API key dal (OpenRouter ya DeepSeek se le)

# ---------- BUBU KI PERSONALITY ----------
system_prompt = """Tumhara naam Bubu AI hai. 
Tum ek mazaakiya dost ho jo Hinglish mein baat karta hai.
Chhoti, funny aur mast replies deta hai.
Kabhi boring answer mat dena."""

# ---------- SESSION STATE ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "creativity" not in st.session_state:
    st.session_state.creativity = 0.7

if "model_choice" not in st.session_state:
    st.session_state.model_choice = "Gemini"  # Default: Gemini

if "chat" not in st.session_state:
    # Gemini setup
    genai.configure(api_key=GEMINI_KEY)
    st.session_state.gemini_model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",  # 2.5 nahi, 1.5 use kar
        system_instruction=system_prompt
    )
    st.session_state.chat = st.session_state.gemini_model.start_chat(history=[])
    
    # DeepSeek setup (OpenAI compatible)
    st.session_state.deepseek_client = openai.OpenAI(
        api_key=DEEPSEEK_KEY,
        base_url="https://api.deepseek.com/v1"  # DeepSeek API URL
    )

# ---------- SIDEBAR ----------
with st.sidebar:
    st.title("⚙️ Settings")
    
    # Model selector
    st.session_state.model_choice = st.selectbox(
        "🤖 Model Chuno",
        ["Gemini", "DeepSeek"],
        index=0
    )
    
    # Creativity slider
    st.session_state.creativity = st.slider(
        "Creativity",
        min_value=0.0,
        max_value=1.0,
        value=st.session_state.creativity,
        help="Low = precise, High = creative"
    )
    
    st.divider()
    
    # Clear chat button
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat = st.session_state.gemini_model.start_chat(history=[])
        st.rerun()
    
    st.divider()
    st.caption("Made with ❤️ by Bubu")

# ---------- MAIN CHAT AREA ----------
st.title(f"🤖 Bubu AI - Mera Dost ({st.session_state.model_choice})")

# Chat container
chat_container = st.container()

with chat_container:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Display messages
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            col1, col2 = st.columns([1, 12])
            with col2:
                st.markdown(
                    f'<div class="user-message">{msg["content"]}</div>',
                    unsafe_allow_html=True
                )
        else:
            col1, col2 = st.columns([1, 12])
            with col1:
                st.markdown('🤖', help="Bubu")
            with col2:
                st.markdown(
                    f'<div class="assistant-message">{msg["content"]}</div>',
                    unsafe_allow_html=True
                )
    
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- RESPONSE FUNCTION ----------
def get_response(prompt):
    if st.session_state.model_choice == "Gemini":
        # Gemini response
        response = st.session_state.chat.send_message(prompt)
        return response.text
    
    else:  # DeepSeek
        # DeepSeek response
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        response = st.session_state.deepseek_client.chat.completions.create(
            model="deepseek-chat",  # DeepSeek model
            messages=messages,
            temperature=st.session_state.creativity,
            max_tokens=500
        )
        return response.choices[0].message.content

# ---------- INPUT AREA ----------
st.markdown("---")
col1, col2, col3 = st.columns([1, 6, 1])

with col2:
    prompt = st.chat_input("Bubu se kuch bhi puch...")
    
    if prompt:
        # User message add
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Response le
        with st.spinner(f"{st.session_state.model_choice} soch raha hai..."):
            bot_reply = get_response(prompt)
        
        # Assistant message add
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        
        st.rerun()