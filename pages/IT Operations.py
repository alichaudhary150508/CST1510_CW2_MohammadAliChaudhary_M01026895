import streamlit as st
import pandas as pd
import os
import openai  # OpenRouter via OpenAI SDK
import plotly.express as px  # For plotting charts

# Page title and icon
st.set_page_config(
    page_title="IT Operations",
    page_icon="💻",
)

# DIRECTORY SAFETY for IT Tickets
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "DATA"))
IT_TICKETS_CSV_PATH = os.path.join(DATA_DIR, "it_tickets.csv")
os.makedirs(DATA_DIR, exist_ok=True)

# SESSION SAFETY (login check)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None

if not st.session_state.logged_in or not st.session_state.username:
    st.error("You must be logged in to view this page.")
    if st.button("Go to Login Page"):
        st.switch_page("Home.py")
    st.stop()

# OPENROUTER / OpenAI Client Configuration
if "OPENAI_API_KEY" not in st.secrets:
    st.error("API key is missing. Please set OPENAI_API_KEY in secrets.")
    st.stop()

openrouter_api_key = st.secrets["OPENAI_API_KEY"]
openai.api_key = openrouter_api_key
openai.api_base = "https://openrouter.ai/api/v1"


# LOAD IT TICKETS CSV
@st.cache_data
def load_it_tickets():
    """Loads it_tickets.csv or returns an empty DataFrame."""
    expected_cols = [
        "ticket_id", "timestamp", "priority", "status",
        "category", "subject", "description", "assigned_to"
    ]

    if not os.path.exists(IT_TICKETS_CSV_PATH):
        st.warning(f"CSV not found at `{IT_TICKETS_CSV_PATH}` — creating a new one.")
        df = pd.DataFrame(columns=expected_cols)
        df.to_csv(IT_TICKETS_CSV_PATH, index=False)
        return df

    try:
        df = pd.read_csv(IT_TICKETS_CSV_PATH)

        # Ensure all expected columns exist
        for col in expected_cols:
            if col not in df.columns:
                df[col] = None

        # Fix timestamp
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

        return df

    except Exception as e:
        st.error(f"Failed to load CSV: {e}")
        return pd.DataFrame(columns=expected_cols)


# Load IT tickets into session
if "df_it_tickets" not in st.session_state:
    st.session_state.df_it_tickets = load_it_tickets()

df_it_tickets = st.session_state.df_it_tickets

# IT Tickets PAGE UI
st.title("📊 IT Tickets Records")
st.write(f"Welcome, **{st.session_state.username}**! Manage and analyze IT tickets.")

# IT Tickets TABLE DISPLAY
st.subheader("📋 IT Ticket Table")

# Search functionality
search_term = st.text_input("Search for an incident (subject, category, assigned_to, etc.):")

# Filtering the DataFrame based on the search term
if search_term:
    filtered_df = df_it_tickets[
        df_it_tickets.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)
    ]
else:
    filtered_df = df_it_tickets  # If no search term, show all tickets

if not filtered_df.empty:
    st.dataframe(filtered_df)  # Display filtered IT tickets
else:
    st.warning("No incidents found matching the search criteria.")

# BUTTON TO REFRESH THE TABLE
if st.button("Refresh IT Tickets Table"):
    st.session_state.df_it_tickets = load_it_tickets()  # Reload tickets from CSV
    st.success("IT Tickets Table has been refreshed.")

# ADD TICKET FORM
st.subheader("➕ Add New IT Ticket")
with st.form(key="add_ticket_form"):
    ticket_subject = st.text_input("Subject of the IT Ticket")
    ticket_category = st.text_input("Category (Network, Hardware, etc.)")
    ticket_priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
    ticket_status = st.selectbox("Status", ["Open", "In Progress", "Resolved", "Closed"])
    ticket_assigned_to = st.text_input("Assigned To")
    ticket_description = st.text_area("Details of the Incident")

    submitted = st.form_submit_button("Add Ticket")

    if submitted:
        if not all([ticket_subject, ticket_category, ticket_priority, ticket_status, ticket_assigned_to,
                    ticket_description]):
            st.error("❌ All fields are required.")
        else:
            new_ticket = {
                "ticket_id": int(df_it_tickets["ticket_id"].max() + 1) if not df_it_tickets.empty else 1000,
                "timestamp": pd.to_datetime("now"),
                "priority": ticket_priority,
                "status": ticket_status,
                "category": ticket_category,
                "subject": ticket_subject,
                "assigned_to": ticket_assigned_to,
                "description": ticket_description
            }

            new_ticket_df = pd.DataFrame([new_ticket])
            df_it_tickets = pd.concat([df_it_tickets, new_ticket_df], ignore_index=True)

            df_it_tickets["timestamp"] = pd.to_datetime(df_it_tickets["timestamp"], errors="coerce")
            df_it_tickets.to_csv(IT_TICKETS_CSV_PATH, index=False)

            # Update the session state
            st.session_state.df_it_tickets = df_it_tickets
            st.success("✅ Ticket added successfully!")

# DELETE TICKET FEATURE
st.subheader("🗑️ Delete an IT Ticket")

ticket_id_to_delete = st.text_input("Enter Ticket ID to Delete:")

if st.button("Delete Ticket") and ticket_id_to_delete:
    try:
        # Convert input to integer for matching ticket_id
        ticket_id_to_delete = int(ticket_id_to_delete)
        # Check if the ticket_id exists in the DataFrame
        if ticket_id_to_delete in df_it_tickets["ticket_id"].values:
            # Remove the row with the matching ticket_id
            df_it_tickets = df_it_tickets[df_it_tickets["ticket_id"] != ticket_id_to_delete]
            # Save the updated DataFrame to the CSV file
            df_it_tickets.to_csv(IT_TICKETS_CSV_PATH, index=False)

            # Update the session state with the new DataFrame
            st.session_state.df_it_tickets = df_it_tickets
            st.success(f"✅ Ticket with ID {ticket_id_to_delete} has been deleted.")
        else:
            st.error(f"❌ Ticket ID {ticket_id_to_delete} not found.")
    except ValueError:
        st.error("❌ Please enter a valid numeric Ticket ID.")
    except Exception as e:
        st.error(f"❌ Error while deleting ticket: {e}")

# AI ASSISTANT for IT Tickets
st.subheader("🤖 IT Tickets AI Assistant")

ticket_text = df_it_tickets.head(40).to_csv(index=False)  # First 40 rows for AI input

# Chat history for AI assistant
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": "You are an IT support assistant. Analyze IT tickets and provide suggestions."
        }
    ]

# "Clear Chat" button
if st.button("Clear Chat"):
    st.session_state.messages = st.session_state.messages[:1]  # Keep only the system message
    st.rerun()  # Rerun the app to reset the chat history

# Display the chat history as new messages appear
for msg in st.session_state.messages:
    if msg["role"] != "system":
        st.chat_message(msg["role"]).markdown(msg["content"])

# New message input for the user
prompt = st.chat_input("Ask the IT Assistant...")

# Handle user message and AI response
if prompt:
    # Display the user's message in the chat box
    st.chat_message("user").markdown(prompt)

    # Append the new user message to the session state
    st.session_state.messages.append({"role": "user", "content": prompt})

    api_messages = st.session_state.messages + [
        {"role": "system", "content": f"Here is the IT tickets dataset (first 40 rows):\n\n{ticket_text}"}
    ]

    try:
        response = openai.ChatCompletion.create(
            model="openai/gpt-3.5-turbo",
            messages=api_messages,
            temperature=0.7,
            max_tokens=500
        )

        # Get the AI's response
        ai_msg = response.choices[0].message["content"]

        # Display the assistant's message in the chat box
        st.chat_message("assistant").markdown(ai_msg)

        # Append the assistant's response to the session state
        st.session_state.messages.append({"role": "assistant", "content": ai_msg})

    except Exception as e:
        st.error(f"Error from OpenRouter API: {e}")

# --- Added Bar and Pie Charts at the Bottom of the Page ---

# Bar chart for IT ticket priority distribution
priority_counts = df_it_tickets['priority'].value_counts()

# Plot the bar chart for priority distribution
fig_bar = px.bar(
    x=priority_counts.index,
    y=priority_counts.values,
    labels={'x': 'Priority', 'y': 'Number of Tickets'},
    title="IT Ticket Priority Distribution"
)
st.plotly_chart(fig_bar)

# Pie chart for IT ticket status distribution
status_counts = df_it_tickets['status'].value_counts()

# Plot the pie chart for status distribution
fig_pie = px.pie(
    names=status_counts.index,
    values=status_counts.values,
    title="IT Ticket Status Distribution"
)
st.plotly_chart(fig_pie)