# MCCIA MSME Helpline Chatbot 💬

This repository contains the source code for a Streamlit-based chatbot designed to assist MSMEs (Micro, Small, and Medium Enterprises) with queries related to MCCIA (Mahratta Chamber of Commerce Industries and Agriculture) services, government schemes, financing, compliance, and other relevant topics.

The chatbot utilizes Google's Gemini API for natural language understanding and response generation, enhanced with a Retrieval-Augmented Generation (RAG) system that fetches relevant information from a custom FAQ list stored in a published Google Sheet.

## ✨ Features

*   **Conversational AI:** Powered by Google Gemini (specifically `gemini-1.5-flash`).
*   **Context-Aware:** Maintains conversation history within a user session using Gemini's `ChatSession`.
*   **FAQ Integration (RAG):** Retrieves relevant information from a user-managed Google Sheet containing FAQs to provide specific, curated answers.
*   **Direct Answers:** Instructed to synthesize information from FAQs and general knowledge without explicitly mentioning the source ("Based on FAQs...").
*   **Custom UI:** Includes a fixed header with MCCIA branding (logo and link) and starter topic buttons for common query areas.
*   **Theming:** Uses Streamlit's theming (`.streamlit/config.toml`) for a custom look (defaults to White/Blue).
*   **Query Logging:** Records all user queries with timestamps and session IDs to a local `query_log.csv` file for analysis.
*   **Feedback Logging:** Allows users to provide thumbs-up/down feedback on bot responses, logging the query, response, feedback, timestamp, and session ID to `feedback_log.csv`.
*   **Session Tracking:** Assigns a unique ID to each user session for easier log analysis.

## 📋 Requirements

*   **Python:** 3.8+
*   **Google Cloud Account:** Required to obtain a Google Gemini API Key.
*   **Google Account:** Required to create and manage the FAQ Google Sheet.
*   **Required Python Packages:** Listed in `requirements.txt`.

## 🚀 Setup and Installation

1.  **Clone the Repository:**
    ```bash
    git clone <your-repository-url>
    cd <repository-directory>
    ```

2.  **Create a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    # Activate the environment:
    # Windows:
    venv\Scripts\activate
    # macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(You'll need to create a `requirements.txt` file - see below)*

4.  **Set Up Environment Variables:**
    *   Obtain a Google Gemini API Key from [Google AI Studio](https://aistudio.google.com/app/apikey).
    *   Create a file named `.env` in the root project directory.
    *   Add your API key to the `.env` file:
        ```dotenv
        # .env
        GOOGLE_API_KEY=YOUR_GOOGLE_API_KEY_HERE
        ```
    *   **(For Deployment):** When deploying to platforms like Streamlit Cloud, set the `GOOGLE_API_KEY` as a secret in the platform's settings instead of using a `.env` file.

5.  **Set Up FAQ Google Sheet:**
    *   Create a new Google Sheet.
    *   Ensure the **first row** contains the exact column headers: `Domain`, `Question`, `Solution`, `Key Words`.
    *   Populate the sheet with your FAQ data. Ensure the `Key Words` column contains relevant, comma-separated keywords for each FAQ.
    *   Go to `File` > `Share` > `Publish to web`.
    *   Select the sheet containing your FAQs.
    *   Choose `Comma-separated values (.csv)` as the format.
    *   Click `Publish` and copy the generated URL.

## ⚙️ Configuration

1.  **Update `ChatApp.py` Constants:**
    *   Replace the placeholder URL in the `GOOGLE_SHEET_FAQ_URL` constant with the actual published CSV URL you copied in the setup step.
    *   Optionally, update `LOGO_URL` and `MCCIA_URL` with the correct links for your branding.

2.  **Configure Theme (Optional):**
    *   Create a folder named `.streamlit` in the root project directory.
    *   Inside `.streamlit`, create a file named `config.toml`.
    *   Add theme settings (example below uses White/Blue):
        ```toml
        # .streamlit/config.toml
        [theme]
        primaryColor="#0d6efd"
        backgroundColor="#FFFFFF"
        secondaryBackgroundColor="#F0F2F6"
        textColor="#333333"
        # font="sans serif"
        ```

## ▶️ Running the App

1.  Ensure your virtual environment is activated.
2.  Navigate to the project directory in your terminal.
3.  Run the Streamlit app:
    ```bash
    streamlit run ChatApp.py
    ```
4.  The app should open automatically in your web browser.

## 📊 Logging

This application creates two CSV files in the same directory where it's run:

*   **`query_log.csv`:** Logs every query submitted by users.
    *   Columns: `timestamp`, `session_id`, `query`
*   **`feedback_log.csv`:** Logs feedback provided via the thumbs-up/down buttons.
    *   Columns: `timestamp`, `session_id`, `query`, `response`, `feedback`

**Note on Deployment:** When deployed on platforms like Streamlit Cloud, these local CSV files might be ephemeral (lost on app restarts). For persistent logging in deployed environments, consider modifying the logging functions to write to an external database or a cloud storage service (like Google Sheets using the `gspread` library, requiring additional setup).

## `requirements.txt`

Create a file named `requirements.txt` in the root of your repository with the following content:

```txt
streamlit
google-generativeai
python-dotenv
pandas
# uuid (built-in, not needed here)
# csv (built-in, not needed here)
# re (built-in, not needed here)
# asyncio (built-in, not needed here)
# os (built-in, not needed here)
# datetime (built-in, not needed here)
