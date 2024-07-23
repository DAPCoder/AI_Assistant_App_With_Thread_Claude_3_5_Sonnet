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

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    user_input = st.chat_input("Say something")

    if user_input:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Create a new thread if it doesn't exist
        if not st.session_state.thread_id:
            thread = client.beta.threads.create()
            st.session_state.thread_id = thread.id

        # Add user message to the thread
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
        with st.spinner("AI is thinking..."):
            while run.status != "completed":
                run = client.beta.threads.runs.retrieve(
                    thread_id=st.session_state.thread_id,
                    run_id=run.id
                )

        # Retrieve and display the assistant's response
        messages = client.beta.threads.messages.list(thread_id=st.session_state.thread_id)
        assistant_response = None
        for message in reversed(messages.data):
            if message.role == "assistant":
                assistant_response = message.content[0].text.value
                break
        
        if assistant_response:
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            with st.chat_message("assistant"):
                st.markdown(assistant_response)

if __name__ == "__main__":
    main()

For claude
I want to create a database for this application. The database is going to 
store username, password and thread_id. i also need the passwords to be 
stored securely using hash format. I want a sidebar element on the left 
that would log users in with their user name and password. If user is 
not in the database, I want you to create the new user,  create a thread 
and assign that thread to the user, if user is in the database, I want you 
to retrieve  the thread_id after logging them in with their password. 
That thread_id will then be used for the conversation. Based on these
    requirements, rewrite the entire application.