import json
from difflib import get_close_matches
import streamlit as st
import google.generativeai as genai

# Configure Gemini securely
genai.configure(api_key=st.secrets["API_KEY"])

FILE_PATH = "chatbot.json"
MODEL_NAME = "gemini-2.5-flash"

st.set_page_config(page_title="🤖 AI Chatbot", page_icon="💡", layout="wide")
st.title("📚 AI Study Helper Chatbot")

def load_kb():
    try:
        with open(FILE_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"questions": []}

def save_kb(data):
    with open(FILE_PATH, "w") as f:
        json.dump(data, f, indent=4)

def get_best_match(q, questions):
    matches = get_close_matches(q.lower(), [x["question"].lower() for x in questions], n=1, cutoff=0.6)
    return matches[0] if matches else None

def get_answer_from_kb(match_text, kb_questions):
    for item in kb_questions:
        if item["question"].lower() == match_text:
            return item["answer"]
    return None

def ask_gemini(q):
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        res = model.generate_content(q)
        return res.text.strip()
    except Exception as e:
        return f"Gemini Error: {e}"

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "kb" not in st.session_state:
    st.session_state.kb = load_kb()

kb_questions = st.session_state.kb["questions"]

# Display chat history
for role, content in st.session_state.messages:
    avatar = "💡" if role == "assistant" else "user"
    with st.chat_message(role, avatar=avatar):
        st.markdown(content, unsafe_allow_html=True)

# Chat input
if prompt := st.chat_input("Ask your question..."):
    st.session_state.messages.append(("user", prompt))
    with st.chat_message("user"):
        st.markdown(prompt)

    match_text = get_best_match(prompt, kb_questions)
    if match_text:
        answer = get_answer_from_kb(match_text, kb_questions)
        source = " (Local KB)"
    else:
        answer = ask_gemini(prompt)
        source = " (Gemini AI)"
        if not answer.startswith("Gemini Error"):
            kb_questions.append({"question": prompt, "answer": answer})
            save_kb(st.session_state.kb)

    full_response = f"{answer}\n\n<small><i>{source}</i></small>"
    st.session_state.messages.append(("assistant", full_response))
    with st.chat_message("assistant", avatar="💡"):
        st.markdown(full_response, unsafe_allow_html=True)