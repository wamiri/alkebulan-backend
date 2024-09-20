import asyncio
import os

import streamlit as st
from utils.file_readers import read_file
from utils.file_uploaders import upload_file
from utils.workflow import RagDataWorkflow


async def run_workflow(documents):
    workflow = RagDataWorkflow()
    result = await workflow.run(documents=documents)
    return result


def pipeline(files):
    documents = list()
    for file in files:
        bytes_data = file.read()
        filename, file_extension = upload_file(bytes_data, file.name)
        documents += read_file(filename, file_extension)

    query_engine = asyncio.run(run_workflow(documents))
    st.session_state["query_engine"] = query_engine


def upload_tab():
    st.header("Upload")
    uploaded_files = st.file_uploader(
        label="Upload your file(s)",
        accept_multiple_files=True,
    )

    if uploaded_files:
        pipeline(uploaded_files)


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

        if st.session_state.get("query_engine") is not None:
            response = st.session_state["query_engine"].query(prompt)
        else:
            response = (
                "The query engine is not initialized yet. Please upload files first."
            )

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
