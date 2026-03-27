import streamlit as st
import requests
import json
import uuid
import time
import pandas as pd

# --------------------------------------------------------------------------------
# Streamlit Page Config
# --------------------------------------------------------------------------------
st.set_page_config(
    page_title="Mobillor AI Agent Dashboard",
    page_icon="🧠",
    layout="wide",

    
)
st.markdown("""
    <style>
        /* Hide Streamlit top toolbar */
        [data-testid="stToolbar"] {
            display: none !important;
        }
    </style>
""", unsafe_allow_html=True)


# --------------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------------
API_BASE_URL = "http://localhost:8000"
APP_NAME = "demo_agents"

# --------------------------------------------------------------------------------
# Initialize Session State
# --------------------------------------------------------------------------------
if "user_id" not in st.session_state:
    st.session_state.user_id = f"user-{uuid.uuid4()}"

if "session_id" not in st.session_state:
    st.session_state.session_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "sql_query" not in st.session_state:
    st.session_state.sql_query = None

if "query_result" not in st.session_state:
    st.session_state.query_result = None


# --------------------------------------------------------------------------------
# Helper Functions
# --------------------------------------------------------------------------------
def create_session():
    """Create a new session with the SQL agent."""
    session_id = f"session-{int(time.time())}"
    response = requests.post(
        f"{API_BASE_URL}/apps/{APP_NAME}/users/{st.session_state.user_id}/sessions/{session_id}",
        headers={"Content-Type": "application/json"},
        data=json.dumps({}),
    )

    if response.status_code == 200:
        st.session_state.session_id = session_id
        st.session_state.messages = []
        st.session_state.sql_query = None
        st.session_state.query_result = None
        return True
    else:
        st.error(f"❌ Failed to create session: {response.text}")
        return False


# --------------------------------------------------------------------------------
# Auto-create session on app start
# --------------------------------------------------------------------------------
if st.session_state.session_id is None:
    create_session()


# --------------------------------------------------------------------------------
# Sidebar (Styled Like ChatGPT)
# --------------------------------------------------------------------------------
# with st.sidebar:
#     st.header("📚 Chats")

#     # New chat button
#     if st.button("🆕 New Chat"):
#         create_session()
#         st.success("✨ New chat started!")
#         st.rerun()

#     st.divider()
#     st.caption("💡 Connected to ADK Server at port 8000")

with st.sidebar:
    st.header("📚 Chats")
    if st.session_state.session_id:
        st.success(f"Active session: {st.session_state.session_id}")
        if st.button("➕ New Session"):
            create_session()
    else:
        st.warning("No active session")
        if st.button("➕ Create Session"):
            create_session()

    st.divider()
    st.caption("💡 Connected to the Agent")

# --------------------------------------------------------------------------------
# Header Section
# --------------------------------------------------------------------------------
st.markdown(
    """
    <div style="
        background: linear-gradient(90deg, #1f2937, #111827);
        padding: 1.2rem 2rem;
        border-radius: 1rem;
        text-align: center;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
    ">
        <h1 style="color:#f9fafb; font-size:2.1rem;">🧠 MOBILLOR'S AI AGENT DASHBOARD 🧠 </h1>
        <h3 style="color:#f9fafb; margin-top:-0.3rem;">Welcome! I’m BIMO  — your intelligent assistant.</h3>
        <h5 style="color:#f9fafb; margin-top:-0.3rem;">Hi, How can I assist you today?</h5>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<br>", unsafe_allow_html=True)


# --------------------------------------------------------------------------------
# Chat Interface
# --------------------------------------------------------------------------------
chat_container = st.container()

with chat_container:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.markdown(f"**You:** {msg['content']}")
        else:
            with st.chat_message("assistant"):
                st.markdown(msg["content"])


# --------------------------------------------------------------------------------
# Auto-scroll to latest message
# --------------------------------------------------------------------------------
st.markdown(
    """
    <script>
    var chatContainer = window.parent.document.querySelector('.stChatMessage:last-child');
    if (chatContainer) {
        chatContainer.scrollIntoView({behavior: "smooth"});
    }
    </script>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------------------------------------
# User Input Area — message shown immediately
# --------------------------------------------------------------------------------
if st.session_state.session_id:
    user_input = st.chat_input("Type your prompt and press Enter...")

    if user_input:
        # Show message instantly
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Save for next rerun
        st.session_state["pending_message"] = user_input

        st.rerun()

else:
    st.info("👈 Create a session to start chatting.")

# --------------------------------------------------------------------------------
# PROCESS PENDING MESSAGE
# --------------------------------------------------------------------------------
if "pending_message" in st.session_state:
    msg = st.session_state.pending_message
    del st.session_state["pending_message"]

    with st.spinner("🤖 Agent is thinking and executing your query..."):
        try:
            response = requests.post(
                f"{API_BASE_URL}/run",
                headers={"Content-Type": "application/json"},
                data=json.dumps({
                    "app_name": APP_NAME,
                    "user_id": st.session_state.user_id,
                    "session_id": st.session_state.session_id,
                    "new_message": {"role": "user", "parts": [{"text": msg}]},
                }),
                timeout=120,
            )
        except Exception as e:
            st.error(f"❌ Request failed: {e}")
            st.stop()

    if response.status_code != 200:
        st.error(f"Please refresh the page and try again! {response.text}")
        st.stop()

    # ===============================
    # UNIVERSAL ADK EVENT PARSER
    # ===============================
    try:
        events = response.json()
    except Exception as e:
        st.error(f"❌ Failed to parse backend response: {e}")
        st.code(response.text)
        st.stop()

    assistant_message = None
    sql_query = None
    query_result = None

    if isinstance(events, list):
        for event in events:

            # ----------- MODEL OUTPUT -----------
            if "response" in event:
                resp = event["response"]

                if "output_text" in resp:
                    assistant_message = resp["output_text"]

                elif "model_response" in resp and "output_text" in resp["model_response"]:
                    assistant_message = resp["model_response"]["output_text"]

                # function call (new ADK)
                if "function_call" in resp:
                    func = resp["function_call"]
                    if func.get("name") == "execute-sql":
                        sql_query = func.get("arguments", {}).get("query", "")
                        query_result = resp.get("result", None)

                # older ADK functionResponse
                if "functionResponse" in resp:
                    fr = resp["functionResponse"]
                    if fr.get("name") == "execute-sql":
                        sql_query = fr.get("arguments", {}).get("query", "")
                        query_result = fr.get("response", {}).get("result", None)

            # ----------- FALLBACK TEXT -----------
            if "content" in event:
                parts = event["content"].get("parts", [])
                for p in parts:
                    if "text" in p:
                        assistant_message = p["text"]

    # Save results to session
    if assistant_message:
        st.session_state.messages.append({"role": "assistant", "content": assistant_message})

    if sql_query:
        st.session_state.sql_query = sql_query

    if query_result:
        st.session_state.query_result = query_result

    st.rerun()








# --------------------------------------------------------------------------------
# SQL & Result Display
# --------------------------------------------------------------------------------
if st.session_state.sql_query:
    st.markdown("### 🧾 Generated SQL Query")
    st.code(st.session_state.sql_query, language="sql")

if st.session_state.query_result:
    st.markdown("### 📊 Query Result")
    try:
        if isinstance(st.session_state.query_result, list):
            df = pd.DataFrame(st.session_state.query_result)
            st.dataframe(df, use_container_width=True, height=400)
        else:
            st.write(st.session_state.query_result)
    except Exception as e:
        st.error(f"Error displaying result: {e}")







