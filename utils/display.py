import streamlit as st

def chat_display(role, content):
    with st.chat_message(role):
        st.markdown(content, unsafe_allow_html=True)