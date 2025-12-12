import pandas as pd
import sqlite3
from app.data.db import connect_database


def connect_database(db_path="DATA/intelligence.db"):
    """Connect to the SQLite database."""
    return sqlite3.connect(db_path)


def create_incidents_table():
    """Create the cyber_incidents table if it doesn't exist."""
    conn = connect_database()
    cursor = conn.cursor()

    # SQL query to create the table
    create_table_query = """
    CREATE TABLE IF NOT EXISTS cyber_incidents (
        incident_id INTEGER PRIMARY KEY,
        timestamp TEXT,
        severity TEXT,
        category TEXT,
        status TEXT,
        description TEXT,
        incident_type TEXT
    )
    """

    # Execute the query to create the table
    cursor.execute(create_table_query)
    conn.commit()  # Commit the transaction
    conn.close()  # Close the connection


def insert_incident(incident_id, timestamp, severity, category, status, description, incident_type):
    """Insert a new incident if it doesn't already exist."""
    conn = connect_database()
    cursor = conn.cursor()

    # Check if the incident_id already exists
    cursor.execute("SELECT COUNT(*) FROM cyber_incidents WHERE incident_id = ?", (incident_id,))
    if cursor.fetchone()[0] > 0:
        print(f"Incident ID {incident_id} already exists, skipping insert.")
        conn.close()
        return None  # Skip inserting the duplicate incident

    # SQL query to insert incident data
    insert_query = """
        INSERT INTO cyber_incidents 
        (incident_id, timestamp, severity, category, status, description, incident_type)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """

    cursor.execute(insert_query, (incident_id, timestamp, severity, category, status, description, incident_type))
    conn.commit()
    conn.close()  # Close the connection

    return incident_id


def get_all_incidents():
    """Return all incidents as a DataFrame."""
    conn = connect_database()
    query = "SELECT * FROM cyber_incidents ORDER BY incident_id DESC"  # Store the query for readability
    df = pd.read_sql_query(query, conn)  # Execute the query and load results into a DataFrame
    conn.close()  # Close the connection
    return df


def insert_incidents_from_csv(csv_file_path):
    """Insert incidents into the database from a CSV file."""
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_file_path)

    # Check if DataFrame is empty
    if df.empty:
        print("CSV file is empty!")
        return

    # Print the contents of the DataFrame to verify
    print("Data from CSV:", df.head())  # Display first few rows of the DataFrame

    # Insert each row of the DataFrame into the SQLite table
    for _, row in df.iterrows():
        incident_id = row.get('incident_id')
        timestamp = row.get('timestamp')
        severity = row.get('severity')
        category = row.get('category')
        status = row.get('status')
        description = row.get('description')
        incident_type = row.get('incident_type')

        print(f"Inserting incident: {incident_id}, {description}")  # Debugging output

        insert_incident(
            incident_id=incident_id,
            timestamp=timestamp,
            severity=severity,
            category=category,
            status=status,
            description=description,
            incident_type=incident_type
        )

    print("All incidents inserted successfully!")


# Create the table if it doesn't exist
create_incidents_table()

# Example usage: Insert incidents from a CSV file into the database
csv_file_path = r'C:\Users\ali08\PycharmProjects\CourseworkAttempt\DATA\cyber_incidents.csv'
insert_incidents_from_csv(csv_file_path)

# Fetch all incidents from the database
incidents_df = get_all_incidents()
print("Incidents from DB:", incidents_df)