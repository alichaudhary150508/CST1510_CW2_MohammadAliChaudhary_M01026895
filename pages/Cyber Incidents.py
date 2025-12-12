import streamlit as st
import pandas as pd
import os
import openai
import plotly.express as px

# Page title and icon
st.set_page_config(
    page_title="Cyber Incidents",
    page_icon="🛡️",
)

# Directory safety
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "DATA"))
CSV_PATH = os.path.join(DATA_DIR, "cyber_incidents.csv")
os.makedirs(DATA_DIR, exist_ok=True)

# Session safety (login check)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None

if not st.session_state.logged_in or not st.session_state.username:
    st.error("You must be logged in to view this page.")
    if st.button("Go to Login Page"):
        st.switch_page("Home.py")
    st.stop()

# OPENROUTER Client Configuration
if "OPENAI_API_KEY" not in st.secrets:
    st.error("API key is missing. Please set OPENAI_API_KEY in secrets.")
    st.stop()

openrouter_api_key = st.secrets["OPENAI_API_KEY"]
openai.api_key = openrouter_api_key
openai.api_base = "https://openrouter.ai/api/v1"

# Load CSV
@st.cache_data
def load_incidents():
    """Loads cyber_incidents.csv or returns an empty DataFrame."""
    expected_cols = [
        "incident_id", "timestamp", "incident_type", "severity",
        "category", "status", "description"
    ]

    if not os.path.exists(CSV_PATH):
        st.warning(f"CSV not found at `{CSV_PATH}` — creating a new one.")
        df = pd.DataFrame(columns=expected_cols)
        df.to_csv(CSV_PATH, index=False)
        return df

    try:
        df = pd.read_csv(CSV_PATH)

        # Ensure all expected columns exist
        for col in expected_cols:
            if col not in df.columns:
                df[col] = None

        # fix timestamp
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

        return df

    except Exception as e:
        st.error(f"Failed to load CSV: {e}")
        return pd.DataFrame(columns=expected_cols)

# Load into session
if "df" not in st.session_state:
    st.session_state.df = load_incidents()

df = st.session_state.df

# Page UI
st.title("📊 Cyber Incident Records")
st.write(f"Welcome, **{st.session_state.username}**! Explore and analyze cybersecurity incidents.")

# Refresh table button
if st.button("Refresh Table"):
    st.session_state.df = load_incidents()  # Reload data from CSV
    df = st.session_state.df

# Main table display with search bar
st.subheader("Cyber Incident Table")

# Search Bar
search_query = st.text_input(
    "Search Incidents",
    placeholder="Search by ID, type, category, severity, status, description..."
)

# Apply filtering
if search_query:
    query = search_query.lower()
    filtered_df = df[df.apply(lambda row: row.astype(str).str.lower().str.contains(query).any(), axis=1)]
else:
    filtered_df = df

# Display filtered or full table
if not filtered_df.empty:
    st.dataframe(filtered_df)
else:
    st.warning("No incidents match your search.")

# Delete incident feature
st.subheader("🗑️ Delete an Incident")

incident_id_to_delete = st.text_input("Enter Incident ID to Delete:")

if st.button("Delete Incident") and incident_id_to_delete:
    try:
        # Convert input to integer for matching incident_id
        incident_id_to_delete = int(incident_id_to_delete)

        if incident_id_to_delete in df["incident_id"].values:
            # Delete row
            df = df[df["incident_id"] != incident_id_to_delete]
            df.to_csv(CSV_PATH, index=False)

            st.session_state.df = df
            st.success(f"Incident with ID {incident_id_to_delete} has been deleted.")
        else:
            st.error(f"Incident ID {incident_id_to_delete} not found.")
    except ValueError:
        st.error("Please enter a valid numeric Incident ID.")
    except Exception as e:
        st.error(f"Error while deleting incident: {e}")

# Add incident
st.subheader("➕ Add New Incident")

with st.form(key="add_incident_form"):
    incident_type = st.text_input("Incident Type (Phishing, Malware)")
    incident_category = st.text_input("Category (Network, Application)")
    incident_severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
    incident_status = st.selectbox("Status", ["Open", "In Progress", "Resolved", "Closed"])
    incident_description = st.text_area("Details of the Incident")

    submitted = st.form_submit_button("Add Incident")

    if submitted:
        if not all([incident_type, incident_category, incident_severity, incident_status, incident_description]):
            st.error("All fields are required.")
        else:
            new_incident = {
                "incident_id": int(df["incident_id"].max() + 1) if not df.empty else 1000,
                "timestamp": pd.to_datetime("now"),
                "incident_type": incident_type,
                "severity": incident_severity,
                "category": incident_category,
                "status": incident_status,
                "description": incident_description
            }

            new_incident_df = pd.DataFrame([new_incident])
            df = pd.concat([df, new_incident_df], ignore_index=True)

            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
            df.to_csv(CSV_PATH, index=False)

            st.session_state.df = df
            st.success("Incident added successfully!")

# Charts
severity_counts = df['severity'].value_counts()

fig_bar = px.bar(
    x=severity_counts.index,
    y=severity_counts.values,
    labels={'x': 'Severity', 'y': 'Number of Incidents'},
    title="Incident Severity Distribution"
)
st.subheader("Incident Severity Distribution")
st.plotly_chart(fig_bar)

category_counts = df['category'].value_counts()

fig_pie = px.pie(
    names=category_counts.index,
    values=category_counts.values,
    title="Incident Category Distribution"
)
fig_pie.update_traces(textinfo="percent+label", pull=[0.1, 0, 0, 0])
st.subheader("Incident Category Distribution")
st.plotly_chart(fig_pie)


# AI assistant
st.subheader("Cybersecurity AI Assistant")

def df_to_text(dframe):
    return dframe.head(40).to_csv(index=False)

incident_text = df_to_text(df)

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                "You are a cybersecurity expert assistant. Analyze cyber incidents, "
                "detect threat patterns, map to MITRE ATT&CK, and provide actionable advice."
            )
        }
    ]

if st.button("Clear Chat"):
    st.session_state.messages = st.session_state.messages[:1]
    st.rerun()

for msg in st.session_state.messages:
    if msg["role"] != "system":
        st.chat_message(msg["role"]).markdown(msg["content"])

prompt = st.chat_input("Ask the Cybersecurity AI Assistant...")

if prompt:
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    api_messages = st.session_state.messages + [
        {
            "role": "system",
            "content": f"Here is the cyber incident dataset (first 40 rows):\n\n{incident_text}"
        }
    ]

    try:
        response = openai.ChatCompletion.create(
            model="openai/gpt-3.5-turbo",
            messages=api_messages,
            temperature=0.7,
            max_tokens=500
        )

        ai_msg = response.choices[0].message["content"]
        st.chat_message("assistant").markdown(ai_msg)
        st.session_state.messages.append({"role": "assistant", "content": ai_msg})

    except Exception as e:
        st.error(f"Error from OpenRouter API: {e}")