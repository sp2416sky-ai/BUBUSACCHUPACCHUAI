import os
import streamlit as st
import google.generativeai as genai
import openai

# ================= API KEYS (STREAMLIT SECRETS) =================
GEMINI_KEY = os.getenv("GOOGLE_API_KEY")
DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY")

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Bubu AI",
    page_icon="🤖",
    layout="wide"
)

# ================= CSS =================
st.markdown("""
<style>
.user-message {
    background-color:#007AFF;
    color:white;
    padding:10px 15px;
    border-radius:20px 20px 5px 20px;
    max-width:70%;
    margin:5px 0;
    margin-left:auto;
}
.assistant-message {
    background-color:#E9ECEF;
    color:black;
    padding:10px 15px;
    border-radius:20px 20px 20px 5px;
    max-width:70%;
    margin:5px 0;
}
.chat-container {
    padding:20px;
    margin-bottom:80px;
}
</style>
""", unsafe_allow_html=True)

# ================= PERSONALITY =================
system_prompt = """Tumhara naam Bubu AI hai.
Tum ek mazaakiya Hinglish dost ho.
Chhoti funny replies do.
Kabhi boring mat banna."""

# ================= SESSION STATE =================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "model_choice" not in st.session_state:
    st.session_state.model_choice = "Gemini"

if "creativity" not in st.session_state:
    st.session_state.creativity = 0.7

# ================= MODEL SETUP =================
if "models_loaded" not in st.session_state:

    if GEMINI_KEY:
        genai.configure(api_key=GEMINI_KEY)
        st.session_state.gemini_model = genai.GenerativeModel(
            model_name="gemini-1.5-flash"
        )

    if DEEPSEEK_KEY:
        st.session_state.deepseek_client = openai.OpenAI(
            api_key=DEEPSEEK_KEY,
            base_url="https://api.deepseek.com/v1"
        )

    st.session_state.models_loaded = True

# ================= SIDEBAR =================
with st.sidebar:
    st.title("⚙️ Settings")

    st.session_state.model_choice = st.selectbox(
        "🤖 Model Chuno",
        ["Gemini", "DeepSeek"],
        index=0
    )

    st.session_state.creativity = st.slider(
        "Creativity",
        0.0, 1.0,
        st.session_state.creativity
    )

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    st.caption("Made with ❤️ by Bubu")

# ================= UI =================
st.title(f"🤖 Bubu AI ({st.session_state.model_choice})")

st.markdown('<div class="chat-container">', unsafe_allow_html=True)

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(
            f'<div class="user-message">{msg["content"]}</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="assistant-message">{msg["content"]}</div>',
            unsafe_allow_html=True
        )

st.markdown('</div>', unsafe_allow_html=True)

# ================= RESPONSE FUNCTION =================
def get_response(prompt):

    # ===== GEMINI =====
    if st.session_state.model_choice == "Gemini":

        if not GEMINI_KEY:
            return "⚠️ Gemini API key missing."

        response = st.session_state.gemini_model.generate_content(
            f"{system_prompt}\nUser: {prompt}"
        )
        return response.text

    # ===== DEEPSEEK =====
    else:

        if not DEEPSEEK_KEY:
            return "⚠️ DeepSeek API key missing."

        messages = [
            {"role":"system","content":system_prompt},
            {"role":"user","content":prompt}
        ]

        response = st.session_state.deepseek_client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=st.session_state.creativity,
            max_tokens=500
        )

        return response.choices[0].message.content

# ================= INPUT =================
prompt = st.chat_input("Bubu se kuch bhi puch...")

if prompt:

    st.session_state.messages.append({"role":"user","content":prompt})

    with st.spinner(f"{st.session_state.model_choice} soch raha hai..."):
        reply = get_response(prompt)

    st.session_state.messages.append({"role":"assistant","content":reply})

    st.rerun()
