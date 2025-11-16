class Page:
    title = 'Dashboard'
    def run(self, app):
        import streamlit as st
        st.header('Sample Dashboard Page')
        st.write('This is a sample page auto-discovered. Add more pages under /pages to extend.')
