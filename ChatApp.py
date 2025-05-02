import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import asyncio

# --- Local Imports ---
# Ensure faqs.py with FAQS list and find_relevant_faqs function exists
try:
    from faqs import FAQS, find_relevant_faqs
except ImportError:
    st.error("Error: faqs.py not found. Please ensure it exists in the same directory.")
    # Define dummy FAQS if file not found, so app can partially run
    FAQS = [{"question": "Sample Q", "answer": "Sample A", "keywords": ["sample"]}]
    def find_relevant_faqs(query, faqs, threshold=1): return []
    st.warning("Using dummy FAQ data as faqs.py was not found.")

# --- Configuration ---
load_dotenv() # Load environment variables from .env file
API_KEY = os.getenv("GOOGLE_API_KEY") # Get the API key

# --- Constants ---
MODEL_NAME = "gemini-1.5-flash" # Or your preferred Gemini model
SYSTEM_INSTRUCTION = """You are a helpful consultant working at MCCIA (Mahratta Chamber of Commerce Industries and Agriculture).
Your role is to assist member MSMEs (Micro, Small, and Medium Enterprises) with their queries.
Be concise and straight to the point. Provide information in small, digestible steps.
If the user's query seems related to the provided FAQ context, prioritize using that information accurately.
If the FAQs don't cover the query, use your general knowledge but maintain the MCCIA persona.
After providing a piece of information, ask if the user needs clarification or the next step, unless the query is fully resolved.
Keep responses brief.NEVER SAY THE USER That you cannot help with something
"""
# --- URLs ---
# !!! IMPORTANT: Replace these placeholder URLs with your actual MCCIA links !!!
LOGO_URL = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSrC5v-vbzb2FOFmpu4jdB_6lEoX01jHNwjJA&s" # REPLACE with actual logo URL
MCCIA_URL = "https://www.mcciapune.com/" # REPLACE with actual MCCIA homepage URL

# --- Initialize Google Gemini ---
if not API_KEY:
    # Stop the app if the API key is missing
    st.error("Error: GOOGLE_API_KEY not found. Please set it in the .env file.")
    st.stop()

try:
    # Configure the Gemini library with the API key
    genai.configure(api_key=API_KEY)
    # Create the generative model instance, providing the model name and system instructions
    model = genai.GenerativeModel(
        MODEL_NAME,
        system_instruction=SYSTEM_INSTRUCTION
        # Optional: Adjust safety settings if needed
    )
except Exception as e:
    # Display an error and stop if model initialization fails
    st.error(f"Error configuring Google Gemini: {e}")
    st.stop()


# --- Streamlit App Layout and Logic ---

# Configure page settings (must be the first Streamlit command)
# The title here sets the browser tab title
st.set_page_config(page_title="MCCIA MSME Helpline", layout="wide")

# --- Custom Fixed Header (CSS Injection) ---
# This CSS defines the look and fixed behavior of the header bar
st.markdown(
    f"""
    <style>
        /* Style for the fixed header */
        .fixed-header {{
            position: fixed; /* Keep header fixed at the top */
            top: 0;
            left: 0;
            right: 0;
            width: 100%;
            z-index: 999; /* Ensure it's above other content */
            background-color: #ffffff; /* White background (matches theme) */
            padding: 10px 25px; /* Adjust padding as needed */
            border-bottom: 1px solid #dddddd; /* Lighter border */
            box-shadow: 0 2px 4px rgba(0,0,0,0.05); /* Softer shadow */
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        /* Style for the logo */
        .header-logo img {{
            height: 45px; /* Adjust logo size */
            margin-right: 15px;
            vertical-align: middle; /* Helps alignment */
        }}
        /* Style for the title text */
        .header-title {{
            font-size: 1.6em; /* Adjust title size */
            font-weight: 600; /* Slightly bolder */
            color: #333333; /* Dark text (matches theme) */
            margin: 0;
            vertical-align: middle; /* Helps alignment */
        }}
        /* Style for the navigation link */
        .header-link a {{
            color: #0d6efd; /* Blue link (matches primaryColor) */
            text-decoration: none;
            font-weight: 500;
            font-size: 0.95em;
            padding: 5px 10px;
            border: 1px solid transparent; /* Placeholder for potential hover effect */
            border-radius: 5px;
            transition: background-color 0.2s ease, color 0.2s ease;
        }}
        .header-link a:hover {{
            text-decoration: none;
             background-color: #e7f1ff; /* Light blue background on hover */
            color: #0a58ca; /* Darker blue on hover */
        }}
        /* Add padding to the top of the main app content to prevent overlap with fixed header */
        /* Adjust padding-top value if header height changes */
        div[data-testid="stAppViewContainer"] > section:first-of-type {{
            padding-top: 80px; /* Increased padding slightly */
        }}
         /* Optionally hide the default Streamlit hamburger menu header */
        header[data-testid="stHeader"] {{
            display: none;
        }}
    </style>
    """,
    unsafe_allow_html=True # Required to apply the custom CSS
)

# --- Custom Fixed Header (HTML Injection) ---
# This HTML creates the actual header elements using the styles defined above
st.markdown(
    f"""
    <div class="fixed-header">
        <div style="display: flex; align-items: center;"> <!-- Left group: Logo + Title -->
            <div class="header-logo">
                <a href="{MCCIA_URL}" target="_blank"><img src="{LOGO_URL}" alt="MCCIA Logo"></a>
            </div>
            <div class="header-title">
                MSME Helpline Chat
            </div>
        </div>
        <div class="header-link"> <!-- Right group: Link -->
            <a href="{MCCIA_URL}" target="_blank">Visit MCCIA Website</a>
        </div>
    </div>
    """,
    unsafe_allow_html=True # Required to render the HTML
)

# --- Main Chat Interface Area ---
# The st.title() is removed as the title is now in the custom header
# st.caption("Your text-based assistant for MSME-related queries.") # Optional: Keep if needed below header

# --- Session State Initialization ---
# Initialize chat history for display if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Welcome to the MCCIA MSME Helpline! How can I assist you today?"}]

# Initialize the Gemini chat session object for context persistence if it doesn't exist
if "gemini_chat_session" not in st.session_state:
    st.session_state.gemini_chat_session = model.start_chat(history=[])

# --- Display Chat History ---
# Iterate through the stored messages and display them
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        # The appearance of these messages will be influenced by the theme in config.toml
        st.write(message["content"])

# --- Text Input Area ---
# Use st.chat_input for the text entry fixed at the bottom
user_input = st.chat_input("Ask your question here...")

# --- Process Input and Generate Response ---
if user_input:
    # 1. Add User Message to Display History
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # 2. Find Relevant FAQs (RAG Step)
    relevant_faqs = find_relevant_faqs(user_input, FAQS)
    faq_context_str = "No specific FAQ context found."
    if relevant_faqs:
        faq_context_str = "Relevant FAQ Context:\n" + "\n\n".join([f"Q: {faq['question']}\nA: {faq['answer']}" for faq in relevant_faqs])
        # Optional: Display FAQ context for debugging
        # with st.expander("ℹ️ Using FAQ Context"):
        #     st.info(faq_context_str)

    # 3. Prepare Prompt for Gemini (including RAG context)
    prompt_with_context = f"{faq_context_str}\n\nUser Query:\n{user_input}"

    # 4. Send Prompt to Gemini using Chat Session for Context
    try:
        chat = st.session_state.gemini_chat_session
        with st.spinner("Thinking..."): # Show loading indicator
            response = chat.send_message(
                prompt_with_context,
            )

        # 5. Process and Display Bot Response
        bot_response_text = response.text
        st.session_state.messages.append({"role": "assistant", "content": bot_response_text})
        with st.chat_message("assistant"):
            st.write(bot_response_text)

    except Exception as e:
        # Handle errors during API call or response generation
        st.error(f"An error occurred: {e}")
        error_msg = "Sorry, I encountered an error processing your request. Please try again or rephrase."
        st.session_state.messages.append({"role": "assistant", "content": error_msg})
        with st.chat_message("assistant"):
            st.write(error_msg)


# --- Sidebar (Optional Information) ---
# st.sidebar.title("About")
# st.sidebar.info(
#     """
#     **MCCIA MSME Helpline Chatbot**

#     Your AI assistant for questions related to MSME support, schemes, and procedures relevant to MCCIA members.
#     """
# )
# # You can add more info or links in the sidebar if needed
# st.sidebar.markdown("[MCCIA Website](https://www.mcciapune.com/)") # Example link

# st.sidebar.markdown("---")
# st.sidebar.header("Developer Notes")
# st.sidebar.info("""
# - **Model:** Google Gemini 1.5 Flash
# - **Context:** Maintained via `ChatSession`.
# - **FAQ:** Basic RAG from `faqs.py`.
# - **Theme:** Set via `.streamlit/config.toml`.
# - **Header:** Custom fixed header via CSS.
# """)