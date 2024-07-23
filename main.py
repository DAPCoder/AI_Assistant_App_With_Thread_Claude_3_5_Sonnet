from openai import OpenAI
from config import OPENAI_API_KEY
from config import assistant_id

client = OpenAI(api_key=OPENAI_API_KEY)

message_thread = client.beta.threads.create(
    messages=[
        {
            "role": "user",
            "content": "Hello, what is AI?"
        },
        {
            "role": "user",
            "content": "How does AI work? Explain it in simple terms."
        },
    ]
)

print(message_thread)

thread_message = client.beta.threads.messages.create(
    "thread_abc123",
    role="user",
    content="How does AI work? Explain it in simple terms.",
)

print(thread_message)

run = client.beta.threads.create_and_run(
    assistant_id="asst_abc123",
    thread={
        "messages": [
            {"role": "user", 
             "content": "Explain deep learning to a 5 year old."}
        ]
    }
)

print(run)

run = client.beta.threads.runs.retrieve(
    thread_id="thread_abc123",
    run_id="run_abc123"
)

print(run)

For Claude:
Write a complete streamlit application that interacts with our assistant