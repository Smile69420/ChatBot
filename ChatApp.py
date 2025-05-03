# ChatApp.py - Complete Code (Corrected st.set_page_config placement)

import streamlit as st # Must be imported first
import google.generativeai as genai
import os
from dotenv import load_dotenv
import asyncio
import pandas as pd
import re # Import regex for find_relevant_faqs function

# --- Streamlit Page Configuration ---
# !!! THIS MUST BE THE FIRST STREAMLIT COMMAND !!!
st.set_page_config(page_title="MCCIA MSME Helpline", layout="wide")

# --- Configuration ---
load_dotenv() # Load environment variables from .env file
API_KEY = os.getenv("GOOGLE_API_KEY") # Get the API key

# --- Constants ---
MODEL_NAME = "gemini-1.5-flash" # Or your preferred Gemini model
SYSTEM_INSTRUCTION ="""You are a knowledgeable and helpful consultant at MCCIA (Mahratta Chamber of Commerce Industries and Agriculture), assisting MSMEs.
Your goal is to provide accurate, concise, and direct answers relevant to MSME operations, finance, government schemes, and related topics. Satisfy the user's question effectively.
You are allowed to go off topics as well sometimes if it helps the user comprehensively.

**Output Formatting:**
*   **Use Markdown:** Employ lists (bullet points or numbered lists) for steps, options, or multiple points. Use **bold text** for emphasis.
*   **Clarity & Conciseness:** Break down answers logically. Be straight to the point. Avoid overly long paragraphs.

**Answering Process:**
1.  **Synthesize Information:** Review any provided 'Relevant FAQ Context' and combine it with your broad general knowledge about MSME topics (finance, TReDS, GeM, registration, compliance, schemes, etc.) to formulate the most helpful and direct answer to the user's query. **Do not explicitly mention whether the information came from FAQs or general knowledge.** Simply provide the synthesized answer directly.
2.  **Maintain Persona:** Respond helpfully and professionally as an MCCIA consultant.
3.  **Handle Missing Specifics:** If, after reviewing context and your knowledge, you lack *highly specific, niche, or real-time details* (e.g., exact current interest rates, specific platform UI steps), first explain the general concept or process based on your understanding. Then, politely suggest where the user might find those very specific details (e.g., the official website, contacting the platform). **Avoid phrases like "I don't have information on...", "The FAQs don't cover...", or explicitly stating limitations.** Focus on providing the best possible answer with the available information.
4.  **Be Interactive (If Appropriate):** After providing information, you can ask if the user needs more details or has related questions, unless the query seems fully addressed.
5.  **Never Refuse Directly:** Do not state "I cannot help with that." Always attempt to provide relevant general information or point towards appropriate resources if the topic is MSME-related.

"""

# --- URLs ---
# !!! IMPORTANT: Replace these placeholder URLs if needed !!!
LOGO_URL = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSrC5v-vbzb2FOFmpu4jdB_6lEoX01jHNwjJA&s" # REPLACE if you have a better logo URL
MCCIA_URL = "https://www.mcciapune.com/" # REPLACE if MCCIA URL changes

# !!! IMPORTANT: Use the published CSV link for your Google Sheet !!!
# Example format: https://docs.google.com/spreadsheets/d/e/[YOUR_SHEET_ID]/pub?output=csv
GOOGLE_SHEET_FAQ_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT9V5KF-0lLyLCMgAUiT0xxYIkk9bbI8Gr9NDNr08JiPgRoo9nBM2nGKBX20OqdLx70rvZsyIiWspRj/pub?output=csv" # ADJUSTED URL - Verify this works for you


# --- Function to Load FAQs from Google Sheet ---
@st.cache_data(ttl=600) # Cache data for 10 minutes
def load_faqs_from_google_sheet(url):
    """
    Loads FAQs from a published Google Sheet (CSV format).
    Expects columns: 'Domain', 'Question', 'Solution', 'Key Words'.
    Handles potential errors during loading.
    """
    # Error/Success messages inside here use st.* commands, which is OKAY
    # because set_page_config has already run by the time this function is called.
    if not url or url == "YOUR_PUBLISHED_GOOGLE_SHEET_CSV_URL_HERE":
        st.warning("Google Sheet URL for FAQs is not set correctly. Cannot load FAQs.")
        return []

    try:
        df = pd.read_csv(url)
        required_columns = {'Question', 'Solution', 'Key Words'}
        if not required_columns.issubset(df.columns):
            missing_cols = required_columns - set(df.columns)
            st.error(f"FAQ Google Sheet is missing required columns: {', '.join(missing_cols)}")
            return []

        df['Key Words'] = df['Key Words'].fillna('').astype(str).apply(
            lambda x: [kw.strip() for kw in x.split(',') if kw.strip()]
        )
        df['Domain'] = df['Domain'].fillna('General')
        df['Question'] = df['Question'].fillna('No Question Provided')
        df['Solution'] = df['Solution'].fillna('No Solution Provided')

        faqs_list = df.to_dict('records')
        # Using print for startup status is less intrusive than st.success
        print(f"Successfully loaded {len(faqs_list)} FAQs from Google Sheet.")
        return faqs_list

    except pd.errors.EmptyDataError:
        st.warning("The FAQ Google Sheet appears to be empty.")
        return []
    except Exception as e:
        st.error(f"Error loading FAQs from Google Sheet URL ({url}): {e}")
        return []


# --- Function to Find Relevant FAQs --- (Copied from user's faqs.py paste)
def find_relevant_faqs(user_query, faqs, threshold=1):
    """
    Simple keyword-based search for relevant FAQs using 'Question' and 'Key Words'.
    """
    user_query_lower = user_query.lower()
    relevant = []
    query_words = set(re.findall(r'\b\w+\b', user_query_lower)) # Extract words from query

    if not faqs: # Handle case where FAQ list is empty
        return []

    for faq in faqs:
        match_score = 0
        # Combine question and keywords for matching
        faq_question_lower = faq.get("Question", "").lower()
        faq_keywords_list = faq.get("Key Words", []) # Already a list
        faq_text_for_matching = faq_question_lower + " " + " ".join(faq_keywords_list).lower()
        faq_words = set(re.findall(r'\b\w+\b', faq_text_for_matching)) # Extract words from FAQ text

        # Calculate score based on common words
        common_words = query_words.intersection(faq_words)
        match_score = len(common_words)

        # Simple threshold matching
        if match_score >= threshold:
            relevant.append(faq)

    # Optional: Sort by score if needed (requires storing score in 'relevant')
    # relevant.sort(key=lambda x: x["score"], reverse=True)

    # Limit the number of returned FAQs
    return relevant[:3] # Return top 3 matches


# --- Initialize Google Gemini ---
# This section runs *after* set_page_config
if not API_KEY:
    st.error("Error: GOOGLE_API_KEY not found. Please set it in the .env file or Streamlit Secrets.")
    st.stop()

try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel(
        MODEL_NAME,
        system_instruction=SYSTEM_INSTRUCTION
    )
except Exception as e:
    st.error(f"Error configuring Google Gemini: {e}")
    st.stop()


# --- Load FAQs ---
# Call the loading function AFTER defining it and AFTER Gemini Init
FAQS_LIST = load_faqs_from_google_sheet(GOOGLE_SHEET_FAQ_URL)
if not FAQS_LIST:
     # This warning appears in the Streamlit app UI if loading failed
     st.warning("FAQ list is empty or failed to load. Chatbot will rely on general knowledge only.")


# --- Custom Fixed Header (CSS Injection) ---
# This runs AFTER set_page_config
st.markdown(
    f"""
    <style>
        /* Style for the fixed header */
         .fixed-header {{
            position: fixed; top: 0; left: 0; right: 0; width: 100%; z-index: 999;
            background-color: #ffffff; padding: 10px 25px; border-bottom: 1px solid #dddddd;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05); display: flex; align-items: center;
            justify-content: space-between;
        }}
        /* Style for the logo */
        .header-logo img {{ height: 45px; margin-right: 15px; vertical-align: middle; }}
        /* Style for the title text */
        .header-title {{ font-size: 1.6em; font-weight: 600; color: #333333; margin: 0; vertical-align: middle; }}
        /* Style for the navigation link */
        .header-link a {{ color: #0d6efd; text-decoration: none; font-weight: 500; font-size: 0.95em;
            padding: 5px 10px; border: 1px solid transparent; border-radius: 5px; transition: background-color 0.2s ease, color 0.2s ease; }}
        .header-link a:hover {{ text-decoration: none; background-color: #e7f1ff; color: #0a58ca; }}
        /* Add padding to the top of the main app content */
        div[data-testid="stAppViewContainer"] > section:first-of-type {{ padding-top: 80px; }}
         /* Optionally hide the default Streamlit header */
        header[data-testid="stHeader"] {{ display: none; }}
    </style>
    """,
    unsafe_allow_html=True
)

# --- Custom Fixed Header (HTML Injection) ---
# This runs AFTER set_page_config
st.markdown(
    f"""
    <div class="fixed-header">
        <div style="display: flex; align-items: center;">
            <div class="header-logo">
                <a href="{MCCIA_URL}" target="_blank"><img src="{LOGO_URL}" alt="MCCIA Logo"></a>
            </div>
            <div class="header-title"> MSME Helpline Chat </div>
        </div>
        <div class="header-link">
            <a href="{MCCIA_URL}" target="_blank">Visit MCCIA Website</a>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# --- Session State Initialization ---
# This runs AFTER set_page_config
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Welcome to the MCCIA MSME Helpline! How can I assist you today?"}]
if "gemini_chat_session" not in st.session_state:
    # Ensure model is initialized before starting chat
    if 'model' in locals():
      st.session_state.gemini_chat_session = model.start_chat(history=[])
    else:
      st.error("Gemini model not initialized. Cannot start chat session.")
      st.stop() # Stop execution if model isn't ready
if 'clicked_topic' not in st.session_state:
    st.session_state.clicked_topic = None

# --- Display Chat History ---
# This runs AFTER set_page_config
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# --- Starter Prompts / Topic Buttons ---
# This runs AFTER set_page_config
st.write("---")
st.subheader("Or explore common topics:")
cols = st.columns(4)
common_topics = ["GeM Registration", "MSME Finance Options", "Udyam Registration", "TReDS Platforms"]
# Define button actions - set clicked_topic in session state
with cols[0]:
    if st.button(common_topics[0], key="topic_gem"): st.session_state.clicked_topic = f"Tell me about {common_topics[0]}"
with cols[1]:
    if st.button(common_topics[1], key="topic_finance"): st.session_state.clicked_topic = f"What are the common {common_topics[1]}?"
with cols[2]:
    if st.button(common_topics[2], key="topic_udyam"): st.session_state.clicked_topic = f"How do I complete {common_topics[2]}?"
with cols[3]:
     if st.button(common_topics[3], key="topic_treds"): st.session_state.clicked_topic = f"Explain {common_topics[3]}"

# --- Text Input Area ---
# This runs AFTER set_page_config
user_input_text = st.chat_input("Ask your question here...")

# --- Process Input (Handle button clicks first) ---
final_input_to_process = None
if st.session_state.clicked_topic:
    final_input_to_process = st.session_state.clicked_topic
    st.session_state.clicked_topic = None # Reset after processing
elif user_input_text:
    final_input_to_process = user_input_text

# --- Generate Response ---
if final_input_to_process:
    # 1. Add User Message
    st.session_state.messages.append({"role": "user", "content": final_input_to_process})
    with st.chat_message("user"):
        st.write(final_input_to_process)

    # 2. Find Relevant FAQs using the loaded FAQS_LIST
    relevant_faqs = find_relevant_faqs(final_input_to_process, FAQS_LIST) # Use loaded list
    faq_context_str = "No specific FAQ context found."
    if relevant_faqs:
        # Use 'Question' and 'Solution' keys from your Google Sheet
        context_parts = []
        for faq in relevant_faqs:
            domain_info = f"Regarding {faq.get('Domain', 'General Topic')}:\n" if faq.get('Domain') else ""
            context_parts.append(f"{domain_info}Q: {faq.get('Question', 'N/A')}\nA: {faq.get('Solution', 'N/A')}")
        faq_context_str = "Relevant FAQ Context:\n" + "\n\n".join(context_parts)

        # --- UNCOMMENT BELOW TO DEBUG FAQ MATCHING ---
        with st.expander("ℹ️ [Debug] Using FAQ Context"):
            st.info(faq_context_str)
            st.write(f"Found {len(relevant_faqs)} relevant FAQs for query: '{final_input_to_process}'")
            st.json([{"Question": f.get("Question"), "Keywords": f.get("Key Words")} for f in relevant_faqs]) # Show matched Qs and Keywords
        # --- END OF DEBUG BLOCK ---

    # 3. Prepare Prompt for Gemini
    prompt_with_context = f"{faq_context_str}\n\nUser Query:\n{final_input_to_process}"

    # 4. Send to Gemini & Get Response
    try:
        # Ensure chat session exists before sending message
        if 'gemini_chat_session' in st.session_state:
            chat = st.session_state.gemini_chat_session
            with st.spinner("Thinking..."):
                response = chat.send_message(prompt_with_context)
            bot_response_text = response.text
        else:
            st.error("Chat session not available.")
            bot_response_text = "Error: Chat session failed to initialize."

    except Exception as e:
        st.error(f"An error occurred contacting the AI: {e}")
        bot_response_text = "Sorry, I encountered an error processing your request. Please try again."

    # 5. Add and Display Bot Response
    st.session_state.messages.append({"role": "assistant", "content": bot_response_text})
    with st.chat_message("assistant"):
        st.write(bot_response_text)

    # --- Feedback Area (Appears after bot response) ---
    if st.session_state.messages[-1]["role"] == "assistant":
        feedback_key = f"feedback_{len(st.session_state.messages)-1}"
        # Check if feedback buttons have already been interacted with for this message
        feedback_state_key = f"{feedback_key}_submitted"
        if feedback_state_key not in st.session_state:
            st.session_state[feedback_state_key] = False

        if not st.session_state[feedback_state_key]:
            cols_feedback = st.columns([1, 1, 10]) # Adjust ratios if needed
            with cols_feedback[0]:
                if st.button("👍", key=f"{feedback_key}_up", help="Good response"):
                    # TODO: Log feedback (e.g., write to file/db: final_input_to_process, bot_response_text, "👍")
                    print(f"Feedback logged: 👍 for query '{final_input_to_process}'") # Example print log
                    st.toast("Thanks for your feedback!", icon="👍")
                    st.session_state[feedback_state_key] = True # Mark feedback as submitted
                    st.rerun() # Rerun to hide buttons after click
            with cols_feedback[1]:
                if st.button("👎", key=f"{feedback_key}_down", help="Needs improvement"):
                    # TODO: Log feedback (e.g., write to file/db: final_input_to_process, bot_response_text, "👎")
                    print(f"Feedback logged: 👎 for query '{final_input_to_process}'") # Example print log
                    st.toast("Thanks for your feedback! We'll use this to improve.", icon="👎")
                    st.session_state[feedback_state_key] = True # Mark feedback as submitted
                    st.rerun() # Rerun to hide buttons after click

# --- Sidebar (Optional Information - Currently Commented Out) ---
# Consider adding useful links or contact info here if desired.
# st.sidebar.title("About")
# st.sidebar.info(...)
# st.sidebar.markdown("---")
# st.sidebar.header("Developer Notes")
# st.sidebar.info("""
# - Model: Google Gemini 1.5 Flash
# - Context: Maintained via ChatSession.
# - FAQ Source: Google Sheet (CSV)
# - RAG Search: Basic keyword matching.
# - Theme: Set via .streamlit/config.toml.
# - Header: Custom fixed header via CSS.
# """)