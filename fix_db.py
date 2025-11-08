# fix_db.py
import sqlite3
import os
from datetime import datetime

def check_and_fix_db():
    db_path = os.path.join('instance', 'site.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check current columns in service table
        cursor.execute("PRAGMA table_info(service);")
        columns = [col[1] for col in cursor.fetchall()]
        print("Current columns in service table:", columns)
        
        # Add missing columns if they don't exist
        if 'slug' not in columns:
            print("Adding missing columns...")
            
            # Get the structure of the current table
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='service';")
            old_table_sql = cursor.fetchone()[0]
            
            # Create a backup of the current table
            cursor.execute("ALTER TABLE service RENAME TO service_old;")
            
            # Create new table with the correct schema
            cursor.execute("""
            CREATE TABLE service (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(100) NOT NULL,
                slug VARCHAR(100) NOT NULL,
                description TEXT,
                content TEXT,
                icon VARCHAR(50),
                image_path VARCHAR(200),
                is_featured BOOLEAN DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                order_position INTEGER DEFAULT 0,
                created_at DATETIME,
                updated_at DATETIME,
                UNIQUE(slug)
            );
            """)
            
            # Get columns that exist in the old table
            cursor.execute("PRAGMA table_info(service_old);")
            old_columns = [col[1] for col in cursor.fetchall()]
            
            # Build the column list for the SELECT statement
            select_columns = []
            for col in ['id', 'title', 'description', 'icon', 'is_active', 'created_at']:
                if col in old_columns:
                    select_columns.append(col)
                else:
                    select_columns.append(f"NULL as {col}")
            
            # Copy data from old table to new table
            cursor.execute(f"""
            INSERT INTO service (
                id, title, slug, description, content, icon, 
                image_path, is_featured, is_active, 
                order_position, created_at, updated_at
            )
            SELECT 
                {', '.join(select_columns)},
                LOWER(REPLACE(COALESCE(title, ''), ' ', '-')) as slug,
                COALESCE(description, '') as content,
                NULL as image_path,
                0 as is_featured,
                COALESCE(is_active, 1) as is_active,
                COALESCE((SELECT MAX(id) FROM service_old) + 1, 1) as order_position,
                COALESCE(created_at, datetime('now')) as created_at,
                datetime('now') as updated_at
            FROM service_old;
            """)
            
            # Drop the old table
            cursor.execute("DROP TABLE service_old;")
            
            print("Successfully updated service table schema!")
        
        # Create index on slug if it doesn't exist
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS ix_service_slug ON service (slug);
        """)
        
        conn.commit()
        print("Database schema is up to date!")
        
    except Exception as e:
        conn.rollback()
        print(f"Error: {str(e)}")
        raise  # Re-raise the exception to see the full traceback
    finally:
        conn.close()

if __name__ == "__main__":
    check_and_fix_db()