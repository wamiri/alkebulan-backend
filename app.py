import os

import streamlit as st

from utils.file_readers import read_file
from utils.file_uploaders import upload_file


def upload_tab():
    st.header("Upload")
    uploaded_files = st.file_uploader(
        label="Upload your file(s)",
        accept_multiple_files=True,
    )

    for uploaded_file in uploaded_files:
        bytes_data = uploaded_file.read()
        filename, file_extension = upload_file(bytes_data, uploaded_file.name)
        st.write(f"{filename}{file_extension} uploaded")


def chat_tab():
    st.header("Chat")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What is your question?"):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        response = f"Echo: {prompt}"

        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})


def main():
    st.title("RAG Pipeline")
    tab1, tab2 = st.tabs(["File Upload", "Chat"])

    with tab1:
        upload_tab()

    with tab2:
        chat_tab()


if __name__ == "__main__":
    main()
