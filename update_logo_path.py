#!/usr/bin/env python3

"""
Script to update company logo path and check current company info
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import create_app, db
    from app.models import CompanyInfo

    def update_logo():
        """Update the company logo path"""

        app = create_app()
        with app.app_context():
            company = CompanyInfo.query.first()

            if company:
                print(f"Current company name: '{company.name}'")
                print(f"Current logo path: '{company.logo_path}'")

                # Update logo path to point to the existing logo file
                company.logo_path = 'uploads/logo/company_logo.jpg'
                db.session.commit()
                print("✅ Logo path updated to: 'uploads/logo/company_logo.jpg'")
                print(f"New logo path: '{company.logo_path}'")
            else:
                print("No company found. Creating new company record...")
                # Create new company if none exists
                company = CompanyInfo(
                    name='KodesMind',
                    tagline='Innovative Software Solutions & Digital Transformation',
                    email='info@kodesmind.com',
                    phone='+1 (555) KODES-01',
                    address='123 Innovation Drive, Tech City, TC 12345',
                    logo_path='uploads/logo/company_logo.jpg',
                    is_active=True
                )
                db.session.add(company)
                db.session.commit()
                print("✅ New company record created with logo path")

    if __name__ == '__main__':
        update_logo()

except ImportError as e:
    print(f"Import error: {e}")
    print("Please make sure you're running this from the correct directory with proper Python path")
except Exception as e:
    print(f"Unexpected error: {e}")
