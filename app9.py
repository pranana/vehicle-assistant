import openai
import streamlit as st
import time
from urllib.parse import parse_qs
import base64
import traceback

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
if "loading_first_response" not in st.session_state:
    st.session_state.loading_first_response = False
if "run_id" not in st.session_state:
    st.session_state.run_id = None
if "first_message_sent" not in st.session_state:
    st.session_state.first_message_sent = False
if "error_message" not in st.session_state:
    st.session_state.error_message = None

# ===================== CUSTOMIZATION SETTINGS =====================
# Colors (using CFMOTO brand colors)
MAIN_BG_COLOR = "#121212"  # Dark background
PRIMARY_COLOR = "#2EAEC2"  # CFMOTO Blue
SECONDARY_COLOR = "#333333"  # Dark gray for inputs
TEXT_COLOR = "#FFFFFF"  # White text
ACCENT_COLOR = "#4B96E6"  # Blue accent

# Text sizes
TITLE_SIZE = "28px"
SUBTITLE_SIZE = "16px"
NORMAL_TEXT_SIZE = "16px"
SMALL_TEXT_SIZE = "14px"

# Customize the Streamlit theme
st.set_page_config(
    page_title="CFMOTO Vehicle Assistant",
    page_icon="🏍️",
    layout="centered"
)

# Add custom CSS for better mobile experience
custom_css = f"""
<style>
    /* Main container customization */
    .stApp {{
        background-color: {MAIN_BG_COLOR};
    }}
    
    /* Headings */
    h1 {{
        font-size: {TITLE_SIZE} !important;
        color: {TEXT_COLOR} !important;
        margin-bottom: 10px !important;
        font-weight: 600 !important;
    }}
    
    p {{
        font-size: {NORMAL_TEXT_SIZE} !important;
        color: {TEXT_COLOR} !important;
    }}
    
    /* Chat message styling */
    .stChatMessage {{
        border-radius: 20px !important;
        padding: 10px !important;
        margin-bottom: 10px !important;
    }}
    
    /* User messages */
    [data-testid="StChatMessageUser"] {{
        background-color: {PRIMARY_COLOR} !important;
    }}
    
    /* Bot messages */
    [data-testid="StChatMessageAssistant"] {{
        background-color: {SECONDARY_COLOR} !important;
    }}
    
    /* Input box */
    .stChatInputContainer {{
        padding: 10px !important;
        border-radius: 25px !important;
        background-color: {SECONDARY_COLOR} !important;
    }}
    
    /* Button styling */
    .stButton button {{
        background-color: {PRIMARY_COLOR} !important;
        color: {TEXT_COLOR} !important;
        border-radius: 20px !important;
        padding: 8px 16px !important;
        border: none !important;
        font-weight: 500 !important;
        width: 100% !important;
    }}
    
    /* Text input */
    .stTextInput input {{
        border-radius: 20px !important;
        background-color: {SECONDARY_COLOR} !important;
        color: {TEXT_COLOR} !important;
        border: 1px solid #555 !important;
        padding: 10px 15px !important;
    }}
    
    /* Info message styling */
    .stAlert {{
        background-color: {SECONDARY_COLOR} !important;
        color: {TEXT_COLOR} !important;
        border: none !important;
        border-radius: 10px !important;
        margin-bottom: 20px !important;
    }}
    
    /* Mobile-specific adjustments */
    @media (max-width: 768px) {{
        .stApp {{
            padding: 10px !important;
        }}
        
        h1 {{
            font-size: {TITLE_SIZE} !important;
            margin-top: 5px !important;
        }}
        
        .stButton button {{
            margin-top: 5px !important;
            margin-bottom: 10px !important;
        }}
    }}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==================== LOGO FUNCTION ====================
# def add_logo():
    # Replace this with a base64 encoded string of your logo
    # Example for a placeholder logo - replace with your actual CFMOTO logo
    # logo_base64 = """
    # iVBORw0KGgoAAAANSUhEUgAAAGQAAAAoCAYAAAAIeF9DAAABhGlDQ1BJQ0MgcHJvZmlsZQAAKJF9
    # kT1Iw0AcxV9TpSIVBzuIOGSoThZERRy1CkWoEGqFVh1MbvqhNGlIUlwcBdeCgx+LVQcXZ10dXAVB
    # 8APE1cVJ0UVK/F9SaBHjwXE/3t173L0DhFqRaVbHOKDptplKxMVMdlUMvCKIAYQxhpjMLGNOkpLw
    # HF/38PH1LsqzvM/9OXqUnMkAn0g8y3TDIt4gnt60dM77xGFWlFTic+IJgy5I/Mh12eU3zkWH/Twz
    # bKRTc4nDxGKujW0tncIMi3FE0tCpb0jHM06ulPMeO/zSsVg16znnPIZzJpW0wosksYiECRnlFFmY
    # ULOSYRpRNY20xDP2eYc/YvmXyKWQqwxGjgVUIprCZg/+B7+7NXMTk24SOA60vjjO+jEI7AKNmudz
    # PjvOiRNAcAY60lL9TQGc/IJp7Wq8AYQ3gcvrvdbkHjD5AH1r0teiKxSkoPRxwfk8J0DvLdCbdXvr
    # nOPwABnq1JRuoDgE+krA+3Wwbh9A4CbQs+bOrXWO0wcgQ7NavgEODkDknC3nc9I72XIg9O74/o2+
    # 3L8HZyNyWf2dUgAAAOxJREFUeNrs14EJwjAUBNDrJLqJi+gkbjIKuomT6Ca6ia6gI7iR2sYPQVqM
    # xLv/IMkhoOTDJdDTCQAAAAAAAOA/jLnuSW5VZ+5t6Zl1X2vOvYfHlOSW5Fpk5rOZwzBMx9/LsTS9
    # XWbB3oo+yMvN66GZU77vjV11S/dz5DLo+Q5JHtUndrPk1rvGDlLv9Rz5buUjpFqPECMrQowsQoys
    # 2ggxsghZGiHPq62KmP2I/WCX5LbR+xXbxX/IwYYUJhshRhYhRlbdWYeRNYcRYmQRYmStQ4iRRYiR
    # dc7yFgIAAAAAAACAXXkBCKaKeaG/7/4AAAAASUVORK5CYII=
    # """
    
    # st.markdown(
    #    f"""
    #    <div style="display: flex; justify-content: center; margin-bottom: 20px;">
    #        <img src="data:image/png;base64,{logo_base64}" width="100">
    #    </div>
    #    """,
        # unsafe_allow_html=True
    # )

# Function to check if a run is active and cancel it if needed
def check_active_run(thread_id):
    try:
        # List all runs for the thread
        runs = client.beta.threads.runs.list(thread_id=thread_id)
        
        # Check if there are any active runs
        for run in runs.data:
            if run.status in ["queued", "in_progress"]:
                try:
                    # Try to cancel the run
                    client.beta.threads.runs.cancel(
                        thread_id=thread_id,
                        run_id=run.id
                    )
                    time.sleep(2)  # Give some time for cancellation to take effect
                except Exception as e:
                    return False
        
        return True
    except Exception as e:
        return False

# Helper function to process assistant messages
def process_assistant_message(message):
    formatted_content = ""
    for content_part in message.content:
        if content_part.type == "text":
            text_value = content_part.text.value
            # Clean up formatting markers
            text_value = text_value.replace("\\n\\n", "\n\n")
            text_value = text_value.replace("\\n", "\n")
            formatted_content += text_value
    
    return formatted_content

# Get API key from secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Get URL parameters
query_params = st.query_params
model_param = query_params.get("model", "")
if model_param and not st.session_state.vehicle_model:
    st.session_state.vehicle_model = model_param

# Add logo at top
# add_logo()

# Chat Title and Description
st.markdown(f"<h1 style='text-align: center;'>Your CFMOTO Vehicle Assistant</h1>", unsafe_allow_html=True)
st.markdown(
    f"""<p style='text-align: center; font-size: {SUBTITLE_SIZE}; margin-bottom: 20px;'>
    Ask any questions regarding your CFMOTO vehicle to this assistant. Keep in mind that 
    the assistant can make mistakes and it's always better to consult your local dealer for support.
    </p>""", 
    unsafe_allow_html=True
)

# Display any error messages
if st.session_state.error_message:
    st.error(st.session_state.error_message)
    st.session_state.error_message = None  # Clear the error after showing it

# Create a container for the main chat interface
chat_container = st.container()

# Get user name if not already provided
if not st.session_state.user_name:
    # If vehicle model is detected, show it
    if st.session_state.vehicle_model:
        st.info(f"Vehicle model detected: {st.session_state.vehicle_model}")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        user_name = st.text_input("What's your name?", key="name_input")
        submit_button = st.button("Start Chat", key="submit_name")
        
        if submit_button and user_name:
            st.session_state.user_name = user_name
            
            if st.session_state.vehicle_model:
                # Create a thread and send first message
                try:
                    # Create a new thread
                    thread = client.beta.threads.create()
                    st.session_state.thread_id = thread.id
                    
                    # Send initial context message
                    initial_message = f"I'm {st.session_state.user_name} and I have a {st.session_state.vehicle_model}."
                    client.beta.threads.messages.create(
                        thread_id=st.session_state.thread_id,
                        role="user",
                        content=initial_message
                    )
                    
                    st.session_state.first_message_sent = True
                    st.session_state.loading_first_response = True
                    st.rerun()
                except Exception as e:
                    error_msg = str(e)
                    st.session_state.error_message = f"Error starting chat: {error_msg}"
                    st.session_state.user_name = None
                    st.rerun()

# Process first response if needed
if st.session_state.first_message_sent and st.session_state.loading_first_response:
    try:
        with st.spinner("Setting up your assistant..."):
            # Check for active runs first
            check_active_run(st.session_state.thread_id)
            
            # Create run to get the first response
            run = client.beta.threads.runs.create(
                thread_id=st.session_state.thread_id,
                assistant_id=assistant_id
            )
            
            st.session_state.run_id = run.id
            
            # Wait for completion with a timeout
            start_time = time.time()
            max_wait_time = 30  # Maximum wait time in seconds
            
            while run.status in ["queued", "in_progress"]:
                # Check if timeout has been reached
                if time.time() - start_time > max_wait_time:
                    st.session_state.error_message = "The assistant is taking too long to respond. Please try again."
                    st.session_state.loading_first_response = False
                    st.session_state.first_message_sent = False
                    st.rerun()
                    break
                
                # Wait a bit before checking status again
                time.sleep(1)
                
                # Get latest run status
                run = client.beta.threads.runs.retrieve(
                    thread_id=st.session_state.thread_id,
                    run_id=run.id
                )
            
            if run.status == "completed":
                # Get the assistant's first message
                messages = client.beta.threads.messages.list(
                    thread_id=st.session_state.thread_id
                )
                
                # Process the assistant's first message
                for message in messages.data:
                    if message.role == "assistant":
                        formatted_content = process_assistant_message(message)
                        
                        # Add assistant message to session
                        st.session_state.messages.append({"role": "assistant", "content": formatted_content})
                        st.session_state.start_chat = True
                        break
            else:
                st.session_state.error_message = f"Error getting response: {run.status}"
                
            st.session_state.loading_first_response = False
            st.rerun()
    except Exception as e:
        error_msg = str(e)
        st.session_state.error_message = f"Error processing response: {error_msg}"
        st.session_state.loading_first_response = False
        st.session_state.first_message_sent = False
        st.rerun()

# Exit Chat Button - only show if chat has started
if st.session_state.start_chat:
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Exit Chat", key="exit_button"):
            st.session_state.messages = []  # Clear the chat history
            st.session_state.start_chat = False  # Reset the chat state
            st.session_state.thread_id = None
            st.session_state.user_name = None
            st.session_state.loading_first_response = False
            st.session_state.run_id = None
            st.session_state.first_message_sent = False
            st.session_state.error_message = None
            st.experimental_rerun()

# Display Chat Messages if Chat is Started
with chat_container:
    if st.session_state.start_chat:
        # Display previous messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # User Input - place in a fixed position container at the bottom
        prompt = st.chat_input("What accessories can I add to my vehicle? What type of maintenance should I do? etc.")
        
        if prompt:
            # Append user message to display
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            try:
                # Make sure there are no active runs
                check_active_run(st.session_state.thread_id)
                
                # Send user message with context to OpenAI
                context_message = f"[Context: I'm {st.session_state.user_name} with a {st.session_state.vehicle_model}] {prompt}"
                client.beta.threads.messages.create(
                    thread_id=st.session_state.thread_id,
                    role="user",
                    content=context_message
                )
                
                # Run the assistant response without overriding instructions
                run = client.beta.threads.runs.create(
                    thread_id=st.session_state.thread_id,
                    assistant_id=assistant_id
                )
                
                st.session_state.run_id = run.id
                
                # Show a spinner while waiting for the response
                with st.spinner("Thinking..."):
                    # Wait for completion
                    while run.status in ["queued", "in_progress"]:
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
                    message for message in messages.data
                    if message.run_id == run.id and message.role == "assistant"
                ]
                
                for message in assistant_messages_for_run:
                    # Process the message content to extract the actual text
                    if hasattr(message, 'content') and len(message.content) > 0:
                        formatted_content = process_assistant_message(message)
                        
                        st.session_state.messages.append({"role": "assistant", "content": formatted_content})
                        with st.chat_message("assistant"):
                            st.markdown(formatted_content)
            
            except Exception as e:
                error_msg = str(e)
                st.session_state.error_message = f"Error processing your request: {error_msg}"
            
            # Rerun to update the UI and move the chat input back to bottom
            st.rerun()
    elif st.session_state.loading_first_response:
        st.spinner("Setting up your assistant...")
    elif not st.session_state.user_name:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("<p style='text-align: center;'>Please enter your name to begin.</p>", unsafe_allow_html=True)

# Add a footer
st.markdown(
    """
    <div style='position: fixed; bottom: 0; left: 0; width: 100%; background-color: #1E1E1E; 
    padding: 5px; text-align: center; font-size: 12px; color: #888;'>
        © 2025 Lab Design. All rights reserved.
    </div>
    """,
    unsafe_allow_html=True
)