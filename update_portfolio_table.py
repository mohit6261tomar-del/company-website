from app import create_app, db
from sqlalchemy import text

def update_portfolio_table():
    app = create_app()
    with app.app_context():
        try:
            # Check if the column exists
            result = db.session.execute(
                text("PRAGMA table_info(portfolio)")
            ).fetchall()
            
            column_exists = any(col[1] == 'date_completed' for col in result)
            
            if not column_exists:
                # Add the column
                db.session.execute(
                    text("ALTER TABLE portfolio ADD COLUMN date_completed DATE")
                )
                print("Added date_completed column to portfolio table.")
                
                # Update existing records to use project_date as date_completed
                db.session.execute(
                    text("UPDATE portfolio SET date_completed = project_date")
                )
                print("Updated existing portfolio entries with project_date values.")
                
                db.session.commit()
            else:
                print("date_completed column already exists.")
                
        except Exception as e:
            print(f"Error updating portfolio table: {e}")
            db.session.rollback()
        finally:
            db.session.close()

if __name__ == '__main__':
    update_portfolio_table()
