import streamlit as st
import pandas as pd
import plotly.express as px

# Page title and icon
st.set_page_config(
    page_title="Dashboard",
    page_icon="🖥️",
)

# Require Login
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.error("You must be logged in to access the Dashboard.")

    # Button to go to Login Page
    if st.button("Go to Login Page"):
        st.switch_page("Home.py")

    st.stop()

st.title("📊 Cyber Incidents Dashboard")

# Load the CSV
df = pd.read_csv(r'C:\Users\ali08\PycharmProjects\CourseworkAttempt\DATA\cyber_incidents.csv')

# Display dataset information for specific columns
st.subheader("Dataset Information")

# Specify the columns of interest
columns_of_interest = ["incident_id", "timestamp", "severity", "category", "status", "description", "incident_type"]

# Display non-null count for each of the specified columns
column_summary = pd.DataFrame({
    "Column Name": columns_of_interest,
    "Non-Null Count": df[columns_of_interest].notnull().sum()
})

# Display the summary
st.dataframe(column_summary)

# Show dataset
st.subheader("Dataset")
st.dataframe(df)

# Pie Chart
st.subheader("Pie Chart – Severity Breakdown")
fig = px.pie(df, names="severity", title="Incidents by Severity")
st.plotly_chart(fig, use_container_width=True)

# Bar Chart
st.subheader("Bar Chart – Category Count")
bar_data = df["category"].value_counts().reset_index()
bar_data.columns = ["category", "count"]

fig = px.bar(bar_data, x="category", y="count", title="Incidents by Category")
st.plotly_chart(fig, use_container_width=True)
