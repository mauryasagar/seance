from pathlib import Path
import streamlit as st
from repo import fetch_repo
from ghost import system_prompt, ask_ghost
from voice import speak

st.set_page_config(page_title="Séance", page_icon="🕯️")
st.markdown(f"<style>{Path('style.css').read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)
st.markdown('<div class="hero"><h1>🕯️ Séance</h1><p>Summon the ghost of an abandoned GitHub repo.<br>It remembers how it died.</p></div>', unsafe_allow_html=True)

def add_reply(msgs):
    reply, err = ask_ghost(msgs)
    if err:
        st.error(err)
        return False
    msgs.append({"role": "assistant", "content": reply})
    audio, verr = speak(reply)
    st.session_state.audio = audio
    if verr:
        st.warning(verr)
    return True

with st.form("summon_form", border=False):
    url = st.text_input("GitHub repo URL", placeholder="https://github.com/mojombo/grit")
    go = st.form_submit_button("Summon")

if go and url:
    with st.spinner("Calling the spirit..."):
        data, err = fetch_repo(url)
        if err:
            st.error(err)
        else:
            msgs = [{"role": "system", "content": system_prompt(data)},
                    {"role": "user", "content": "Introduce yourself and tell me how you died."}]
            if add_reply(msgs):
                st.session_state.msgs = msgs

for m in st.session_state.get("msgs", [])[2:]:
    st.chat_message(m["role"]).write(m["content"])

if st.session_state.get("audio"):
    st.audio(st.session_state.audio, format="audio/wav", autoplay=True)

if "msgs" in st.session_state:
    q = st.chat_input("Ask the ghost...")
    if q:
        st.session_state.msgs.append({"role": "user", "content": q})
        with st.spinner("The ghost is thinking..."):
            ok = add_reply(st.session_state.msgs)
        if ok:
            st.rerun()