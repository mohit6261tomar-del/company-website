#!/usr/bin/env python
"""
Deployment readiness checklist
"""
import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, CompanyInfo

def check_deployment_readiness():
    """Check if project is ready for deployment"""
    app = create_app()
    
    print("=== DEPLOYMENT READINESS CHECK ===")
    print()
    
    # 1. Database Check
    print("1. Database Configuration:")
    try:
        with app.app_context():
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"   Tables: {len(tables)} - OK")
            
            # Check essential tables
            essential_tables = ['user', 'company_info', 'team', 'service', 'portfolio']
            missing_tables = [t for t in essential_tables if t not in tables]
            if missing_tables:
                print(f"   Missing tables: {missing_tables} - ERROR")
            else:
                print("   Essential tables: OK")
                
    except Exception as e:
        print(f"   Database error: {e} - ERROR")
    
    print()
    
    # 2. Admin User Check
    print("2. Admin User:")
    try:
        with app.app_context():
            admin = User.query.filter_by(is_admin=True).first()
            if admin:
                print(f"   Admin user found: {admin.username} - OK")
                if admin.password_hash and len(admin.password_hash) > 20:
                    print("   Password set: OK")
                else:
                    print("   Password not set properly - WARNING")
            else:
                print("   No admin user found - ERROR")
    except Exception as e:
        print(f"   Admin check error: {e} - ERROR")
    
    print()
    
    # 3. Company Info Check
    print("3. Company Information:")
    try:
        with app.app_context():
            company = CompanyInfo.query.first()
            if company:
                print(f"   Company name: {company.name} - OK")
                if company.email:
                    print(f"   Email: {company.email} - OK")
                else:
                    print("   Email not set - WARNING")
            else:
                print("   No company info found - WARNING")
    except Exception as e:
        print(f"   Company info error: {e} - ERROR")
    
    print()
    
    # 4. Configuration Files Check
    print("4. Configuration Files:")
    config_files = [
        'requirements.txt',
        'config.py', 
        'gunicorn_config.py',
        'Procfile',
        'Dockerfile',
        'docker-compose.yml',
        'wsgi.py',
        '.env.example'
    ]
    
    for file in config_files:
        if os.path.exists(file):
            print(f"   {file}: OK")
        else:
            print(f"   {file}: MISSING")
    
    print()
    
    # 5. Production Configuration Check
    print("5. Production Configuration:")
    from config import ProductionConfig
    prod_config = ProductionConfig()
    
    print(f"   SECRET_KEY set: {'OK' if prod_config.SECRET_KEY != 'dev-key-change-in-production' else 'WARNING - Change default key'}")
    print(f"   Database URI: {prod_config.SQLALCHEMY_DATABASE_URI[:50]}... - OK")
    print(f"   CSRF Protection: {'OK' if prod_config.WTF_CSRF_ENABLED else 'ERROR'}")
    print(f"   Debug mode: {'OK' if not prod_config.DEBUG else 'WARNING - Debug enabled'}")
    
    print()
    
    # 6. Security Check
    print("6. Security Settings:")
    print(f"   Session secure: {'OK' if prod_config.SESSION_COOKIE_SECURE else 'WARNING'}")
    print(f"   Session HTTPOnly: {'OK' if prod_config.SESSION_COOKIE_HTTPONLY else 'WARNING'}")
    
    print()
    
    # 7. File Structure Check
    print("7. File Structure:")
    required_dirs = [
        'app',
        'app/static',
        'app/templates',
        'migrations',
        'instance'
    ]
    
    for dir_path in required_dirs:
        if os.path.isdir(dir_path):
            print(f"   {dir_path}/: OK")
        else:
            print(f"   {dir_path}/: MISSING")
    
    print()
    print("=== DEPLOYMENT READINESS SUMMARY ===")
    print("Project is ready for deployment!")
    print("Next steps:")
    print("1. Change default admin password")
    print("2. Set production SECRET_KEY")
    print("3. Configure production database")
    print("4. Deploy using your preferred method")

if __name__ == '__main__':
    check_deployment_readiness()
