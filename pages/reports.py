class Page:
    title = 'Reports'
    def run(self, app):
        import streamlit as st
        st.header('Reports Page')
        st.write('This is a sample reports page.')
