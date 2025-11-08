import os
import sys
from datetime import datetime

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Service

def fix_service_table():
    app = create_app()
    with app.app_context():
        # Get the database URL
        db_url = app.config['SQLALCHEMY_DATABASE_URI']
        print(f"Using database: {db_url}")
        
        # Check if the service table exists
        if not db.engine.dialect.has_table(db.engine, 'service'):
            print("Creating service table...")
            db.create_all()
        
        # Get the table object
        from sqlalchemy import Table, MetaData
        metadata = MetaData()
        metadata.reflect(bind=db.engine)
        
        if 'service' not in metadata.tables:
            print("Service table not found. Creating it...")
            Service.__table__.create(db.engine)
            print("Service table created successfully!")
            return
            
        service_table = metadata.tables['service']
        
        # Check and add missing columns
        columns_to_add = {
            'slug': {'type': db.String(100), 'nullable': False, 'default': '', 'after': 'title'},
            'content': {'type': db.Text, 'nullable': True, 'after': 'description'},
            'image_path': {'type': db.String(200), 'nullable': True, 'after': 'icon'},
            'is_featured': {'type': db.Boolean, 'nullable': False, 'default': False, 'after': 'is_active'},
            'order_position': {'type': db.Integer, 'nullable': False, 'default': 0, 'after': 'is_featured'},
            'updated_at': {'type': db.DateTime, 'nullable': True, 'default': datetime.utcnow, 'onupdate': datetime.utcnow, 'after': 'created_at'}
        }
        
        print("Checking for missing columns...")
        for column_name, column_def in columns_to_add.items():
            if column_name not in service_table.columns:
                print(f"Adding column: {column_name}")
                column_type = column_def['type']
                column = db.Column(column_name, column_type, **{k: v for k, v in column_def.items() if k != 'type'})
                column.table = service_table
                column._set_parent(service_table)
                
                # Create the column using raw SQL for SQLite
                with db.engine.connect() as conn:
                    # SQLite doesn't support ALTER TABLE ADD COLUMN with AFTER
                    # So we'll need to create a new table and copy the data
                    if 'after' in column_def:
                        # Get all column names in order
                        all_columns = [c.name for c in service_table.columns]
                        insert_after = column_def['after']
                        idx = all_columns.index(insert_after) + 1
                        all_columns.insert(idx, column_name)
                        
                        # Generate the new table DDL
                        temp_table_name = f"temp_{service_table.name}"
                        
                        # Create the new table with the new column
                        new_columns = []
                        for col in service_table.columns:
                            new_columns.append(f'"{col.name}" {col.type.compile(db.engine.dialect)}')
                            if col.name == insert_after:
                                new_columns.append(f'"{column_name}" {column_type.compile(db.engine.dialect)}')
                        
                        # Create the new table
                        create_sql = f'''
                        CREATE TABLE {temp_table_name} (
                            {', '.join(new_columns)}
                        )
                        '''
                        conn.execute(create_sql)
                        
                        # Copy data from old table to new table
                        select_columns = [f'"{c.name}"' for c in service_table.columns]
                        if column_name not in select_columns:
                            select_columns.append(f'NULL as "{column_name}"')
                        
                        insert_sql = f'''
                        INSERT INTO {temp_table_name} 
                        SELECT {', '.join(select_columns)} 
                        FROM {service_table.name}
                        '''
                        conn.execute(insert_sql)
                        
                        # Drop the old table
                        conn.execute(f'DROP TABLE {service_table.name}')
                        
                        # Rename the new table
                        conn.execute(f'ALTER TABLE {temp_table_name} RENAME TO {service_table.name}')
                        
                        # Recreate indexes
                        for index in service_table.indexes:
                            index.create(bind=db.engine)
                        
                        print(f"Added column {column_name} after {insert_after}")
                    else:
                        # Simple case: just add the column at the end
                        alter_sql = f'ALTER TABLE {service_table.name} ADD COLUMN "{column_name}" {column_type.compile(db.engine.dialect)}'
                        conn.execute(alter_sql)
                        print(f"Added column {column_name}")
        
        # Update existing rows with default values
        print("Updating existing rows...")
        with db.engine.connect() as conn:
            # Update slug if it's empty or NULL
            conn.execute(f'''
                UPDATE {service_table.name} 
                SET 
                    slug = LOWER(REPLACE(title, ' ', '-')),
                    content = description,
                    is_featured = 0,
                    order_position = id,
                    updated_at = CURRENT_TIMESTAMP
                WHERE slug IS NULL OR slug = '';
            ''')
            
            # Make sure slug is unique by appending id if needed
            conn.execute(f'''
                UPDATE {service_table.name} s1
                SET slug = s1.slug || '-' || s1.id
                WHERE EXISTS (
                    SELECT 1 FROM {service_table.name} s2 
                    WHERE s2.slug = s1.slug 
                    AND s2.id < s1.id
                );
            ''')
        
        # Create unique index on slug if it doesn't exist
        inspector = db.inspect(db.engine)
        indexes = inspector.get_indexes('service')
        slug_index = next((idx for idx in indexes if 'slug' in idx['column_names']), None)
        
        if not slug_index:
            print("Creating unique index on slug column...")
            with db.engine.connect() as conn:
                conn.execute(f'CREATE UNIQUE INDEX ix_service_slug ON {service_table.name} (slug);')
        
        print("Database update complete!")

if __name__ == "__main__":
    fix_service_table()
