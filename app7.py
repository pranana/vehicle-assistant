import openai
import streamlit as st
import time
from urllib.parse import parse_qs

assistant_id = "asst_uOevBb2ecrPVS8DR39MJNE5a"
client = openai

# Initialize session state variables
if "start_chat" not in st.session_state:
    st.session_state.start_chat = False
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "vehicle_model" not in st.session_state:
    st.session_state.vehicle_model = None
if "welcome_shown" not in st.session_state:
    st.session_state.welcome_shown = False

st.set_page_config(page_title="Your CFMOTO Vehicle Assistant", page_icon=":speech_balloon:")

# Get API key from secrets
openai.api_key = st.secrets["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"]

# Get URL parameters
query_params = st.experimental_get_query_params()
model_param = query_params.get("model", [""])[0]
if model_param and not st.session_state.vehicle_model:
    st.session_state.vehicle_model = model_param

# Chat Title and Description
st.title("Your CFMOTO Vehicle Assistant")
st.write("Ask any questions regarding your CFMOTO vehicle to this assistant. Keep in mind that the assistant can make mistakes and it's always better to consult your local dealer for support.")

# User name input if not provided
if not st.session_state.user_name:
    user_name = st.text_input("What's your name?")
    if user_name:
        st.session_state.user_name = user_name
        if st.session_state.vehicle_model:
            st.session_state.start_chat = True
            thread = client.beta.threads.create()
            st.session_state.thread_id = thread.id
            
            # Add welcome message
            welcome_message = f"Hello {st.session_state.user_name}! I'm your vehicle assistant. I see you have a {st.session_state.vehicle_model}. How can I help you today?"
            st.session_state.messages.append({"role": "assistant", "content": welcome_message})
            st.session_state.welcome_shown = True
            st.experimental_rerun()

# If we have a model but no user name yet, show a message
elif st.session_state.vehicle_model and not st.session_state.start_chat:
    st.info(f"Vehicle model detected: {st.session_state.vehicle_model}")

# Start Chat Button (only show if we don't have a user name yet)
if not st.session_state.start_chat and not st.session_state.user_name:
    if st.sidebar.button("Start Chat"):
        st.session_state.start_chat = True
        thread = client.beta.threads.create()
        st.session_state.thread_id = thread.id

# Exit Chat Button
if st.session_state.start_chat and st.button("Exit Chat"):
    st.session_state.messages = []  # Clear the chat history
    st.session_state.start_chat = False  # Reset the chat state
    st.session_state.thread_id = None
    st.session_state.user_name = None
    st.session_state.welcome_shown = False
    st.experimental_rerun()

# Display Chat Messages if Chat is Started
if st.session_state.start_chat:
    if "openai_model" not in st.session_state:
        st.session_state.openai_model = "gpt-4o-mini"
    
    # Display previous messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # User Input
    if prompt := st.chat_input("What accessories can I add to my vehicle? What type of maintenance should I do? etc."):
        
        # Append user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Send user message to OpenAI
        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=prompt
        )
        
        # Run the assistant response
        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=assistant_id,
            instructions=f"The user's name is {st.session_state.user_name} and they have a {st.session_state.vehicle_model} vehicle. Provide helpful information about CFMOTO vehicles."
        )
        
        # Wait for completion
        while run.status != 'completed':
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id,
                run_id=run.id
            )
        
        # Retrieve all messages from the thread
        messages = client.beta.threads.messages.list(
            thread_id=st.session_state.thread_id
        )
        
        # Process and Display the assistant's messages
        assistant_messages_for_run = [
            message for message in messages
            if message.run_id == run.id and message.role == "assistant"
        ]
        
        for message in assistant_messages_for_run:
            # Process the message content to extract the actual text
            if hasattr(message, 'content') and len(message.content) > 0:
                # Handle different content types
                formatted_content = ""
                for content_part in message.content:
                    if content_part.type == "text":
                        text_value = content_part.text.value
                        # Clean up formatting markers
                        text_value = text_value.replace("\\n\\n", "\n\n")
                        text_value = text_value.replace("\\n", "\n")
                        formatted_content += text_value
                
                st.session_state.messages.append({"role": "assistant", "content": formatted_content})
                with st.chat_message("assistant"):
                    st.markdown(formatted_content)
else:
    st.write("Please enter your name to begin.")