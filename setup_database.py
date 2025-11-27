#!/usr/bin/env python
"""
Database setup script for deployment
"""
import os
import sys
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, CompanyInfo, Team, Service, Portfolio, Blog, Career, ContactMessage, JobApplication

def create_admin_user():
    """Create default admin user"""
    admin = User(
        username='admin',
        email='admin@company.com',
        is_admin=True
    )
    admin.set_password('admin123')
    db.session.add(admin)
    print("Created admin user: admin/admin123")

def create_sample_company_info():
    """Create sample company information"""
    company = CompanyInfo(
        name='Your Company Name',
        tagline='Professional Services & Solutions',
        about_us='We are a professional company dedicated to providing excellent services to our clients.',
        address='123 Business Street, City, State 12345',
        email='contact@company.com',
        phone='+1 (555) 123-4567'
    )
    db.session.add(company)
    print("Created company information")

def main():
    """Main setup function"""
    app = create_app()
    
    with app.app_context():
        print("Setting up database...")
        
        # Drop all tables (fresh start)
        db.drop_all()
        print("Dropped existing tables")
        
        # Create all tables
        db.create_all()
        print("Created database tables")
        
        # Create initial data
        create_admin_user()
        create_sample_company_info()
        
        # Commit changes
        db.session.commit()
        print("Database setup completed successfully!")
        
        # Print table information
        print("\nCreated tables:")
        print("- User (admin user created)")
        print("- CompanyInfo (sample data created)")
        print("- Team")
        print("- Service") 
        print("- Portfolio")
        print("- Blog")
        print("- Career")
        print("- ContactMessage")
        print("- JobApplication")

if __name__ == '__main__':
    main()
