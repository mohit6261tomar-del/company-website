from app import create_app, db
from app.models import User
from datetime import datetime
from sqlalchemy import text

def update_database():
    app = create_app()
    with app.app_context():
        # This will create all tables that don't exist
        db.create_all()
        
        # Add last_seen column if it doesn't exist
        try:
            # Check if the column exists
            result = db.session.execute(
                text("PRAGMA table_info(user)")
            ).fetchall()
            
            column_exists = any(col[1] == 'last_seen' for col in result)
            
            if not column_exists:
                # Add the column
                db.session.execute(
                    text("ALTER TABLE user ADD COLUMN last_seen DATETIME")
                )
                print("Added last_seen column to user table.")
                db.session.commit()
            else:
                print("last_seen column already exists.")
                
        except Exception as e:
            print(f"Error checking/adding column: {e}")
            db.session.rollback()
        
        # Update existing users with current timestamp
        try:
            print("Updating existing users...")
            users = User.query.all()
            for user in users:
                if not hasattr(user, 'last_seen') or user.last_seen is None:
                    user.last_seen = datetime.utcnow()
                    db.session.add(user)
            db.session.commit()
            print("Database update complete!")
        except Exception as e:
            print(f"Error updating users: {e}")
            db.session.rollback()

if __name__ == '__main__':
    update_database()
