import sqlite3
import pandas as pd


def connect_database(db_path="DATA/intelligence.db"):
    """Connect to the SQLite database."""
    return sqlite3.connect(db_path)


def create_it_tickets_table():
    """Create the it_tickets table if it doesn't exist."""
    conn = connect_database()  # Use existing connection function
    cursor = conn.cursor()

    # SQL query to create the table
    create_table_query = """
    CREATE TABLE IF NOT EXISTS it_tickets (
        ticket_id INTEGER PRIMARY KEY,
        priority TEXT,
        status TEXT,
        description TEXT,
        assigned_to TEXT,
        created_at TEXT,
        resolution_time_hours INTEGER
    )
    """

    # Execute the query to create the table
    cursor.execute(create_table_query)
    conn.commit()  # Commit the transaction
    conn.close()  # Close the connection


def insert_ticket(ticket_id, priority, description, status, assigned_to,
                  created_at, resolution_time_hours):
    """Insert a new IT ticket if it doesn't already exist."""
    conn = connect_database()  # Use existing connection function
    cursor = conn.cursor()

    # Check if the ticket already exists
    cursor.execute("SELECT COUNT(*) FROM it_tickets WHERE ticket_id = ?", (ticket_id,))
    if cursor.fetchone()[0] > 0:
        print(f"Ticket ID {ticket_id} already exists, skipping insert.")
        conn.close()
        return None  # Optionally return None or the existing ticket's ID

    # SQL query to insert ticket data
    insert_query = """
        INSERT INTO it_tickets
        (ticket_id, priority, status, description, assigned_to,
         created_at, resolution_time_hours)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """

    # Execute the query with parameters
    cursor.execute(insert_query, (ticket_id, priority, status, description, assigned_to,
                                  created_at, resolution_time_hours))

    conn.commit()  # Commit the transaction
    ticket_row_id = cursor.lastrowid  # Get the last inserted row ID
    conn.close()  # Close the connection

    return ticket_row_id


def get_all_tickets():
    """Return all tickets as a DataFrame."""
    conn = connect_database()  # Use existing connection function
    query = "SELECT * FROM it_tickets"  # Store the query for readability
    df = pd.read_sql_query(query, conn)  # Execute the query and load results into a DataFrame
    conn.close()  # Close the connection
    return df


def insert_tickets_from_csv(csv_file_path):
    """Insert tickets into the database from a CSV file."""
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
        ticket_id = row.get('ticket_id')
        priority = row.get('priority')
        status = row.get('status')
        description = row.get('description')
        assigned_to = row.get('assigned to')  # Adjusted for the column name
        created_at = row.get('created_at')  # Adjusted for the column name
        resolution_time_hours = row.get('resolution_time_hours')  # Adjusted for the column name

        print(f"Inserting ticket: {ticket_id}, {description}")  # Debugging output

        insert_ticket(
            ticket_id=ticket_id,
            priority=priority,
            status=status,
            description=description,
            assigned_to=assigned_to,
            created_at=created_at,
            resolution_time_hours=resolution_time_hours
        )

    print("All tickets inserted successfully!")

# Create the table if it doesn't exist
create_it_tickets_table()

# Example usage: Insert tickets from a CSV file into the database
csv_file_path = r'C:\Users\ali08\PycharmProjects\CourseworkAttempt\DATA\it_tickets.csv'
insert_tickets_from_csv(csv_file_path)

# Fetch all tickets from the database
tickets_df = get_all_tickets()
print("Tickets from DB:", tickets_df)