import streamlit as st
import pandas as pd
import os
import openai  # OpenRouter via OpenAI SDK
import plotly.express as px  # For plotting charts

# Page title and icon
st.set_page_config(
    page_title="Data Science",
    page_icon="📉",
)

# DIRECTORY SAFETY for Datasets Metadata
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "DATA"))
DATASETS_METADATA_CSV_PATH = os.path.join(DATA_DIR, "datasets_metadata.csv")
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

# LOAD Datasets Metadata CSV
@st.cache_data
def load_datasets_metadata():
    """Loads datasets_metadata.csv or returns an empty DataFrame."""
    expected_cols = [
        "dataset_id", "name", "rows", "columns", "uploaded_by", "upload_date"
    ]

    if not os.path.exists(DATASETS_METADATA_CSV_PATH):
        st.warning(f"CSV not found at `{DATASETS_METADATA_CSV_PATH}` — creating a new one.")
        df = pd.DataFrame(columns=expected_cols)
        df.to_csv(DATASETS_METADATA_CSV_PATH, index=False)
        return df

    try:
        df = pd.read_csv(DATASETS_METADATA_CSV_PATH)

        # Ensure all expected columns exist
        for col in expected_cols:
            if col not in df.columns:
                df[col] = None

        # Fix upload_date
        df["upload_date"] = pd.to_datetime(df["upload_date"], errors="coerce")

        return df

    except Exception as e:
        st.error(f"Failed to load CSV: {e}")
        return pd.DataFrame(columns=expected_cols)


# Load Datasets Metadata into session
if "df_datasets_metadata" not in st.session_state:
    st.session_state.df_datasets_metadata = load_datasets_metadata()

df_datasets_metadata = st.session_state.df_datasets_metadata

# Datasets Metadata PAGE UI
st.title("📊 Datasets Metadata Records")
st.write(f"Welcome, **{st.session_state.username}**! Manage and analyze datasets metadata.")

# Datasets Metadata TABLE DISPLAY
st.subheader("📋 Datasets Metadata Table")

# Search functionality
search_term = st.text_input("Search for a dataset (name, uploaded_by, etc.):")

# Filtering the DataFrame based on the search term
if search_term:
    filtered_df = df_datasets_metadata[
        df_datasets_metadata.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)
    ]
else:
    filtered_df = df_datasets_metadata  # If no search term, show all datasets

if not filtered_df.empty:
    st.dataframe(filtered_df)  # Display filtered Datasets Metadata
else:
    st.warning("No datasets found matching the search criteria.")

# BUTTON TO REFRESH THE TABLE
if st.button("Refresh Datasets Metadata Table"):
    st.session_state.df_datasets_metadata = load_datasets_metadata()  # Reload datasets from CSV
    st.success("Datasets Metadata Table has been refreshed.")

# ADD DATASET FORM
st.subheader("➕ Add New Dataset")

with st.form(key="add_dataset_form"):
    dataset_name = st.text_input("Dataset Name")
    rows = st.number_input("Number of Rows", min_value=1)
    columns = st.number_input("Number of Columns", min_value=1)
    uploaded_by = st.text_input("Uploaded By")
    upload_date = st.date_input("Upload Date")

    submitted = st.form_submit_button("Add Dataset")

    if submitted:
        if not all([dataset_name, rows, columns, uploaded_by, upload_date]):
            st.error("❌ All fields are required.")
        else:
            new_dataset = {
                "dataset_id": int(
                    df_datasets_metadata["dataset_id"].max() + 1) if not df_datasets_metadata.empty else 1000,
                "name": dataset_name,
                "rows": rows,
                "columns": columns,
                "uploaded_by": uploaded_by,
                "upload_date": pd.to_datetime(upload_date)
            }

            new_dataset_df = pd.DataFrame([new_dataset])
            df_datasets_metadata = pd.concat([df_datasets_metadata, new_dataset_df], ignore_index=True)

            df_datasets_metadata.to_csv(DATASETS_METADATA_CSV_PATH, index=False)

            # Update the session state
            st.session_state.df_datasets_metadata = df_datasets_metadata
            st.success("✅ Dataset added successfully!")

# DELETE DATASET FEATURE
st.subheader("🗑️ Delete a Dataset")

dataset_id_to_delete = st.text_input("Enter Dataset ID to Delete:")

if st.button("Delete Dataset") and dataset_id_to_delete:
    try:
        # Convert input to integer for matching dataset_id
        dataset_id_to_delete = int(dataset_id_to_delete)
        # Check if the dataset_id exists in the DataFrame
        if dataset_id_to_delete in df_datasets_metadata["dataset_id"].values:
            # Remove the row with the matching dataset_id
            df_datasets_metadata = df_datasets_metadata[df_datasets_metadata["dataset_id"] != dataset_id_to_delete]
            # Save the updated DataFrame to the CSV file
            df_datasets_metadata.to_csv(DATASETS_METADATA_CSV_PATH, index=False)

            # Update the session state with the new DataFrame
            st.session_state.df_datasets_metadata = df_datasets_metadata
            st.success(f"✅ Dataset with ID {dataset_id_to_delete} has been deleted.")
        else:
            st.error(f"❌ Dataset ID {dataset_id_to_delete} not found.")
    except ValueError:
        st.error("❌ Please enter a valid numeric Dataset ID.")
    except Exception as e:
        st.error(f"❌ Error while deleting dataset: {e}")

# Bar chart for the number of rows per dataset
rows_counts = df_datasets_metadata['rows'].value_counts()

# Create a bar chart using Plotly
fig_bar = px.bar(
    x=rows_counts.index,
    y=rows_counts.values,
    labels={'x': 'Number of Rows', 'y': 'Number of Datasets'},
    title="Number of Rows per Dataset"
)
st.subheader("📊 Number of Rows per Dataset")
st.plotly_chart(fig_bar)

# Pie chart for the distribution of datasets by "uploaded_by"
uploaded_by_counts = df_datasets_metadata['uploaded_by'].value_counts()

# Create a pie chart using Plotly
fig_pie = px.pie(
    names=uploaded_by_counts.index,
    values=uploaded_by_counts.values,
    title="Dataset Distribution by 'Uploaded By'"
)
fig_pie.update_traces(textinfo="percent+label", pull=[0.1, 0, 0, 0])  # Optional: pulls the first slice out for emphasis
st.subheader("📊 Dataset Distribution by 'Uploaded By'")
st.plotly_chart(fig_pie)

# AI ASSISTANT for Datasets Metadata
st.subheader("🤖 Datasets Metadata AI Assistant")

dataset_text = df_datasets_metadata.head(40).to_csv(index=False)  # First 40 rows for AI input

# Chat history for AI assistant
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": "You are a data expert assistant. Analyze datasets metadata and provide actionable insights."
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
prompt = st.chat_input("Ask the Dataset Metadata Assistant...")

# Handle user message and AI response
if prompt:
    # Display the user's message in the chat box
    st.chat_message("user").markdown(prompt)

    # Append the new user message to the session state
    st.session_state.messages.append({"role": "user", "content": prompt})

    api_messages = st.session_state.messages + [
        {"role": "system", "content": f"Here is the dataset metadata (first 40 rows):\n\n{dataset_text}"}
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