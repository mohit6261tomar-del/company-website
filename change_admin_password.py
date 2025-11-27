#!/usr/bin/env python
"""
Script to change admin password
"""
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

def change_admin_password():
    """Change admin password"""
    app = create_app()
    
    with app.app_context():
        # Get admin user
        admin = User.query.filter_by(is_admin=True).first()
        
        if not admin:
            print("No admin user found!")
            return False
        
        print(f"Current admin user: {admin.username}")
        print(f"Current email: {admin.email}")
        
        # Get new password
        new_password = input("Enter new password: ").strip()
        
        if not new_password or len(new_password) < 6:
            print("Password must be at least 6 characters long!")
            return False
        
        # Confirm password
        confirm_password = input("Confirm new password: ").strip()
        
        if new_password != confirm_password:
            print("Passwords do not match!")
            return False
        
        # Update password
        admin.set_password(new_password)
        db.session.commit()
        
        print(f"Password updated successfully for admin: {admin.username}")
        print(f"New login credentials:")
        print(f"  Username: {admin.username}")
        print(f"  Password: {new_password}")
        
        return True

def reset_admin_to_default():
    """Reset admin to default credentials"""
    app = create_app()
    
    with app.app_context():
        admin = User.query.filter_by(is_admin=True).first()
        
        if not admin:
            print("No admin user found!")
            return False
        
        # Reset to default
        admin.set_password('admin123')
        db.session.commit()
        
        print("Admin password reset to default!")
        print("Username: admin")
        print("Password: admin123")
        
        return True

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--reset':
        reset_admin_to_default()
    else:
        change_admin_password()
