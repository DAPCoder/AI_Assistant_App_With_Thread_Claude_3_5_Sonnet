import streamlit as st
from openai import OpenAI
from config import OPENAI_API_KEY, ASSISTANT_ID

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Streamlit app
def main():
    st.title("AI Assistant Chat")

    # Initialize session state
    if 'thread_id' not in st.session_state:
        st.session_state.thread_id = None
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Chat input
    user_input = st.chat_input("Ask a question...")

    if user_input:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        # Create a thread if it doesn't exist
        if not st.session_state.thread_id:
            thread = client.beta.threads.create()
            st.session_state.thread_id = thread.id

        # Add message to thread
        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=user_input
        )

        # Run the assistant
        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=ASSISTANT_ID
        )

        # Wait for the run to complete
        while run.status != "completed":
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id,
                run_id=run.id
            )

        # Retrieve and display the assistant's response
        messages = client.beta.threads.messages.list(thread_id=st.session_state.thread_id)
        assistant_message = messages.data[0].content[0].text.value

        st.session_state.messages.append({"role": "assistant", "content": assistant_message})
        with st.chat_message("assistant"):
            st.write(assistant_message)

if __name__ == "__main__":
    main()

 For claude
we actually need >>>st.chat_input("Say something") for the chat input   