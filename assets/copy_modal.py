import streamlit as st, os

ASSET_CSS = os.path.join('assets','modal.css')
ASSET_JS = os.path.join('assets','modal.js')

def load_assets():
    try:
        with open(ASSET_CSS,'r',encoding='utf-8') as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except Exception:
        pass
    try:
        with open(ASSET_JS,'r',encoding='utf-8') as f:
            st.components.v1.html(f"<script>{f.read()}</script>", height=1)
    except Exception:
        pass

def open_modal(text, theme='auto'):
    load_assets()
    safe = text.replace('`','\\`')
    st.components.v1.html(f"<script>window.openCopyModal(`{safe}`, '{theme}');</script>", height=1)
