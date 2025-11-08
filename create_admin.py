from app import create_app, db, bcrypt
from app.models import User

def create_admin():
    app = create_app()
    with app.app_context():
        # Check if admin already exists
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print('Admin user already exists. Updating password...')
            admin.set_password('admin123')
            admin.is_admin = True
        else:
            # Create new admin user
            admin = User(
                username='admin',
                email='admin@example.com',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
        
        db.session.commit()
        print('Admin user created/updated successfully!')
        print('Username: admin')
        print('Password: admin123')
        print('\nIMPORTANT: Change this password after first login!')

if __name__ == '__main__':
    create_admin()
