from app import create_app, db
from app.models import Service
import os

def fix_database():
    app = create_app()
    with app.app_context():
        # Get the database path
        db_path = os.path.join(os.path.dirname(__file__), 'instance', 'site.db')
        print(f"Database path: {db_path}")
        
        # Check if the table exists and has the slug column
        inspector = db.inspect(db.engine)
        columns = [column['name'] for column in inspector.get_columns('service')]
        print(f"Current columns in service table: {columns}")
        
        # If slug column doesn't exist, we'll need to recreate the table
        if 'slug' not in columns:
            print("Recreating service table with new schema...")
            
            # Rename existing table
            db.session.execute('ALTER TABLE service RENAME TO service_old')
            
            # Create new table with updated schema
            db.create_all()
            
            # Copy data from old table to new table
            try:
                # Get all records from old table
                result = db.session.execute('SELECT * FROM service_old')
                old_services = [dict(row) for row in result.mappings()]
                
                # Insert into new table
                for service in old_services:
                    # Map old columns to new schema
                    new_service = Service(
                        id=service.get('id'),
                        title=service.get('title'),
                        # Generate slug from title if not exists
                        slug=service.get('slug', service.get('title', '').lower().replace(' ', '-')),
                        description=service.get('description', ''),
                        content=service.get('content', ''),
                        icon=service.get('icon', ''),
                        image_path=service.get('image_path', ''),
                        is_featured=service.get('is_featured', False),
                        is_active=service.get('is_active', True),
                        order_position=service.get('order_position', 0),
                        created_at=service.get('created_at'),
                        updated_at=service.get('updated_at')
                    )
                    db.session.add(new_service)
                
                # Commit the changes
                db.session.commit()
                print("Successfully migrated data to new schema")
                
                # Drop old table
                db.session.execute('DROP TABLE service_old')
                db.session.commit()
                print("Old table dropped successfully")
                
            except Exception as e:
                db.session.rollback()
                print(f"Error during migration: {str(e)}")
                print("Rolling back changes...")
                # Restore original table
                db.session.execute('DROP TABLE IF EXISTS service')
                db.session.execute('ALTER TABLE service_old RENAME TO service')
                db.session.commit()
                print("Original table restored")
        else:
            print("Service table already has the required columns")

if __name__ == '__main__':
    fix_database()
