from pathlib import Path
import streamlit as st
from src.repo import fetch_repo
from src.ghost import system_prompt, ask_ghost
from src.voice import speak

ROOT = Path(__file__).parent

st.set_page_config(page_title="Séance", page_icon="🕯️")
st.markdown(f"<style>{(ROOT / 'static' / 'style.css').read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)
st.markdown((ROOT / "static" / "background.html").read_text(encoding="utf-8"), unsafe_allow_html=True)

st.markdown('<div class="hero"><h1>🕯️ SÉANCE</h1><p>Light a candle. Name a dead repo.<br>Hear it tell you how it died.</p></div>', unsafe_allow_html=True)
st.markdown('<div class="steps"><div class="step"><b>I. SUMMON</b>Paste a dead repo\'s link</div><div class="step"><b>II. LISTEN</b>Its ghost speaks, in a haunted voice</div><div class="step"><b>III. ASK</b>Find out why it died</div></div>', unsafe_allow_html=True)

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
    c1, c2 = st.columns([4, 1])
    url = c1.text_input("GitHub repo URL", placeholder="https://github.com/mojombo/grit", label_visibility="collapsed")
    go = c2.form_submit_button("Summon", use_container_width=True)

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
    st.chat_message(m["role"], avatar="👻" if m["role"] == "assistant" else "🕯️").write(m["content"])

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
        else:
            st.session_state.msgs.pop()

st.markdown('<div class="foot">Powered by open-weight Gemma, running on this machine · voice by ElevenLabs</div>', unsafe_allow_html=True)