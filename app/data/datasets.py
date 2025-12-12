import sqlite3
import pandas as pd

def connect_database(db_path="DATA/intelligence.db"):
    """Connect to the SQLite database."""
    return sqlite3.connect(db_path)

def create_datasets_metadata_table():
    """Create the datasets_metadata table if it doesn't exist."""
    conn = connect_database()
    cursor = conn.cursor()

    # SQL query to create the table
    create_table_query = """
    CREATE TABLE IF NOT EXISTS datasets_metadata (
        dataset_id INTEGER PRIMARY KEY,
        name TEXT,
        rows INTEGER,
        columns INTEGER,
        uploaded_by TEXT,
        upload_date TEXT
    )
    """

    # Execute the query to create the table
    cursor.execute(create_table_query)
    conn.commit()  # Commit the transaction
    conn.close()  # Close the connection

def insert_dataset(dataset_id, name, rows, columns, uploaded_by, upload_date):
    """Insert a new dataset record if it doesn't already exist."""
    conn = connect_database()
    cursor = conn.cursor()

    # Check if the dataset_id already exists
    cursor.execute("SELECT COUNT(*) FROM datasets_metadata WHERE dataset_id = ?", (dataset_id,))
    if cursor.fetchone()[0] > 0:
        print(f"Dataset ID {dataset_id} already exists, skipping insert.")
        conn.close()
        return None  # Skip inserting the duplicate dataset

    # SQL query to insert dataset metadata
    insert_query = """
        INSERT INTO datasets_metadata
        (dataset_id, name, rows, columns, uploaded_by, upload_date)
        VALUES (?, ?, ?, ?, ?, ?)
    """

    cursor.execute(insert_query, (dataset_id, name, rows, columns, uploaded_by, upload_date))
    conn.commit()
    conn.close()  # Close the connection

    return dataset_id

def get_all_datasets():
    """Return all datasets as a DataFrame."""
    conn = connect_database()
    query = "SELECT * FROM datasets_metadata"  # Store query in a variable for readability
    df = pd.read_sql_query(query, conn)  # Read the results into a DataFrame
    conn.close()
    return df

def insert_datasets_from_csv(csv_file_path):
    """Insert datasets into the database from a CSV file."""
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
        dataset_id = row.get('dataset_id')
        name = row.get('name')
        rows = row.get('rows')
        columns = row.get('columns')
        uploaded_by = row.get('uploaded_by')
        upload_date = row.get('upload_date')

        print(f"Inserting dataset: {dataset_id}, {name}")  # Debugging output

        insert_dataset(
            dataset_id=dataset_id,
            name=name,
            rows=rows,
            columns=columns,
            uploaded_by=uploaded_by,
            upload_date=upload_date
        )

    print("All datasets inserted successfully!")


# Create the table if it doesn't exist
create_datasets_metadata_table()

# Example usage: Insert datasets from a CSV file into the database
csv_file_path = r'C:\Users\ali08\PycharmProjects\CourseworkAttempt\DATA\datasets_metadata.csv'
insert_datasets_from_csv(csv_file_path)

# Fetch all datasets from the database
datasets_df = get_all_datasets()
print("Datasets from DB:", datasets_df)