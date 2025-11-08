import sqlite3
import os
from datetime import datetime

def update_database():
    # Path to the SQLite database
    db_path = os.path.join('instance', 'site.db')
    print(f"Updating database at: {os.path.abspath(db_path)}")
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = OFF;")
        cursor.execute("BEGIN TRANSACTION;")
        
        # Check if the service table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='service';
        """)
        
        if cursor.fetchone():
            print("Service table found. Checking schema...")
            
            # Get the current columns
            cursor.execute("PRAGMA table_info(service);")
            columns = [column[1] for column in cursor.fetchall()]
            print(f"Current columns: {columns}")
            
            # Check if we need to add any columns
            new_columns = [
                ('slug', 'VARCHAR(100) NOT NULL UNIQUE', "LOWER(REPLACE(title, ' ', '-'))"),
                ('content', 'TEXT', "description"),
                ('image_path', 'VARCHAR(200)', 'NULL'),
                ('is_featured', 'BOOLEAN', '0'),
                ('order_position', 'INTEGER', 'id'),
                ('updated_at', 'DATETIME', f"'{datetime.now().isoformat()}'")
            ]
            
            for col_name, col_type, default_value in new_columns:
                if col_name not in columns:
                    print(f"Adding column: {col_name}")
                    cursor.execute(f"""
                        ALTER TABLE service 
                        ADD COLUMN {col_name} {col_type} 
                        DEFAULT {default_value};
                    """)
                    
                    # If this is the slug column, update existing rows
                    if col_name == 'slug':
                        cursor.execute("""
                            UPDATE service 
                            SET slug = LOWER(REPLACE(title, ' ', '-'))
                            WHERE slug IS NULL;
                        """)
                    
                    print(f"Column {col_name} added successfully.")
            
            # Commit the changes
            conn.commit()
            print("Database schema updated successfully!")
            
        else:
            print("Service table not found. Creating it...")
            cursor.execute("""
                CREATE TABLE service (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title VARCHAR(100) NOT NULL,
                    slug VARCHAR(100) NOT NULL UNIQUE,
                    description TEXT,
                    content TEXT,
                    icon VARCHAR(50),
                    image_path VARCHAR(200),
                    is_featured BOOLEAN DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1,
                    order_position INTEGER DEFAULT 0,
                    created_at DATETIME,
                    updated_at DATETIME
                );
            """)
            print("Service table created successfully!")
            
    except Exception as e:
        print(f"Error updating database: {e}")
        conn.rollback()
    finally:
        # Re-enable foreign keys and close connection
        cursor.execute("PRAGMA foreign_keys = ON;")
        conn.close()

if __name__ == "__main__":
    update_database()
