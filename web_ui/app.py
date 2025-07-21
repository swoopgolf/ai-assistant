import streamlit as st
import requests
import json

# --- Configuration ---
ORCHESTRATOR_URL = "http://localhost:10200"

# --- Page Setup ---
st.set_page_config(
    page_title="AI Agent System",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Club Management AI Assistant")
st.caption("Ask me anything about sales, the menu, or prices. I'll route your question to the right agent.")

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Helper Functions ---
def call_orchestrator(prompt: str):
    """Sends a prompt to the orchestrator and returns the response."""
    payload = {
        "jsonrpc": "2.0",
        "method": "delegate_task",
        "params": {"task_description": prompt},
        "id": "1"
    }
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(ORCHESTRATOR_URL, data=json.dumps(payload), headers=headers, timeout=60)
        response.raise_for_status() # Raise an exception for bad status codes
        
        # The agent returns a JSON-RPC response, we need to parse it
        json_rpc_response = response.json()
        if "result" in json_rpc_response:
            # The actual result is often nested inside the 'result' key
            result_data = json_rpc_response["result"]
            # The result might still be a JSON string, so we parse it again if needed
            if isinstance(result_data, str):
                try:
                    return json.loads(result_data)
                except json.JSONDecodeError:
                    return {"message": result_data} # Return as is if not valid JSON
            return result_data
        elif "error" in json_rpc_response:
            return {"error": json_rpc_response["error"].get("message", "Unknown error")}
        else:
            return {"error": "Invalid JSON-RPC response from agent."}

    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to connect to the Orchestrator Agent: {e}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}

# --- UI Rendering ---
# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        # Check if the content is a dict and format it
        if isinstance(message["content"], dict):
            st.json(message["content"])
        else:
            st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What would you like to know?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = call_orchestrator(prompt)
            # Check if the response is a dict and format it, otherwise display as text
            if isinstance(response, dict):
                st.json(response)
            else:
                st.markdown(response)
            
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response}) 