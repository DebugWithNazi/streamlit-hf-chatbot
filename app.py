import streamlit as st

import backend
import storage

st.set_page_config(page_title="HF Chatbot", page_icon="💬", layout="centered")


@st.cache_resource(show_spinner="Loading model (first run downloads it)...")
def get_llm():
    return backend.load_llm()


llm = get_llm()


# ---------- Session / resume logic ----------
def open_chat(chat_id: str):
    st.session_state.chat_id = chat_id
    st.session_state.messages = storage.load_chat(chat_id)
    st.query_params["chat"] = chat_id  # survives browser refresh


if "chat_id" not in st.session_state:
    saved = storage.list_chats()
    wanted = st.query_params.get("chat")
    if wanted and any(c["id"] == wanted for c in saved):
        open_chat(wanted)               # resume the chat from the URL
    elif saved:
        open_chat(saved[0]["id"])       # resume the latest chat
    else:
        open_chat(storage.new_chat_id())


# ---------- Sidebar ----------
with st.sidebar:
    st.title("💬 Chats")
    if st.button("➕ New chat", use_container_width=True):
        open_chat(storage.new_chat_id())
        st.rerun()

    st.divider()
    for chat in storage.list_chats():
        col1, col2 = st.columns([5, 1])
        is_current = chat["id"] == st.session_state.chat_id
        label = ("▶ " if is_current else "") + chat["title"]
        if col1.button(label, key=f"open_{chat['id']}", use_container_width=True):
            open_chat(chat["id"])
            st.rerun()
        if col2.button("🗑", key=f"del_{chat['id']}"):
            storage.delete_chat(chat["id"])
            if is_current:
                open_chat(storage.new_chat_id())
            st.rerun()


# ---------- Main chat area ----------
st.header("HuggingFace Chatbot")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Type your message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # st.write_stream renders chunks live and returns the full text
        reply = st.write_stream(backend.stream_reply(llm, st.session_state.messages))

    st.session_state.messages.append({"role": "assistant", "content": reply})
    storage.save_chat(st.session_state.chat_id, st.session_state.messages)
    st.rerun()  # refreshes the sidebar title for new chats