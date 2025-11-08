import sqlite3
import os

def check_database():
    # Path to the SQLite database
    db_path = os.path.join('instance', 'site.db')
    print(f"Checking database at: {os.path.abspath(db_path)}")
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get table info
        cursor.execute("PRAGMA table_info(service);")
        columns = cursor.fetchall()
        print("\nService table columns:")
        for col in columns:
            print(f"- {col[1]} ({col[2]})")
            
        # Get sample data
        cursor.execute("SELECT * FROM service LIMIT 1;")
        row = cursor.fetchone()
        if row:
            print("\nSample service data:")
            cursor.execute("SELECT id, title, slug, is_featured FROM service;")
            for row in cursor.fetchall():
                print(f"ID: {row[0]}, Title: {row[1]}, Slug: {row[2]}, Featured: {row[3]}")
        else:
            print("\nNo services found in the database.")
            
    except Exception as e:
        print(f"Error checking database: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_database()
