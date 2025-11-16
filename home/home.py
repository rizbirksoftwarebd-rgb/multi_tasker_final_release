import streamlit as st
from config import LOGO_PATH
from assets.copy_modal import load_assets, open_modal

class HomePage:
    def __init__(self, app): self.app = app

    def run(self):
        load_assets()
        st.markdown(f"<div class='header'><img src='{LOGO_PATH}' width='140'/><div><h2>Multi-Tasker</h2><p style='margin-top:-8px'>Role-based demo app</p></div></div>", unsafe_allow_html=True)
        st.markdown('---')
        st.markdown("<div class='card'><h3>Your workspace</h3><p>Demo content here.</p></div>", unsafe_allow_html=True)
        if st.button('Show copy modal (demo)'):
            open_modal('This is a demo text to copy.\nYou can paste it anywhere.', theme='auto')
