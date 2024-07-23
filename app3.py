import streamlit as st
import sqlite3
import bcrypt
from openai import OpenAI
from config import OPENAI_API_KEY, ASSISTANT_ID

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Database setup
def init_db():
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, password TEXT, thread_id TEXT)''')
    conn.commit()
    conn.close()

def create_user(username, password):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    thread = client.beta.threads.create()
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute("INSERT INTO users VALUES (?, ?, ?)", (username, hashed_password, thread.id))
    conn.commit()
    conn.close()
    return thread.id

def verify_user(username, password):
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute("SELECT password, thread_id FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    if result and bcrypt.checkpw(password.encode('utf-8'), result[0]):
        return result[1]  # Return thread_id
    return None

# Streamlit app
def main():
    st.title("AI Assistant Chat")

    init_db()

    # Sidebar for login
    with st.sidebar:
        st.header("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            thread_id = verify_user(username, password)
            if thread_id:
                st.session_state.thread_id = thread_id
                st.session_state.username = username
                st.success("Logged in successfully!")
            else:
                st.error("Invalid username or password")
        
        if st.button("Create New User"):
            if username and password:
                try:
                    thread_id = create_user(username, password)
                    st.session_state.thread_id = thread_id
                    st.session_state.username = username
                    st.success("User created successfully!")
                except sqlite3.IntegrityError:
                    st.error("Username already exists")
            else:
                st.error("Please enter a username and password")

    # Main chat area
    if 'thread_id' in st.session_state and 'username' in st.session_state:
        st.write(f"Logged in as: {st.session_state.username}")
        
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
    else:
        st.write("Please log in to start chatting.")

if __name__ == "__main__":
    main()