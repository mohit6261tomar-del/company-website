#!/usr/bin/env python3

"""
Script to update company name to KodesMind with proper error handling
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import create_app, db
    from app.models import CompanyInfo

    def update_company_name():
        """Update the company name to KodesMind"""

        app = create_app()
        with app.app_context():
            try:
                # Check if company exists
                company = CompanyInfo.query.first()

                if company:
                    print(f"Current company name: '{company.name}'")
                    company.name = 'KodesMind'
                    company.tagline = 'Innovative Software Solutions & Digital Transformation'
                    company.email = 'info@kodesmind.com'
                    company.phone = '+1 (555) KODES-01'
                    company.address = '123 Innovation Drive, Tech City, TC 12345'
                    company.about_us = 'KodesMind is a leading technology company specializing in custom software development, digital transformation, and innovative solutions for modern businesses.'

                    db.session.commit()
                    print("✅ Company name updated to 'KodesMind'")
                    print(f"New company name: '{company.name}'")
                else:
                    print("No company found. Creating new company record...")
                    # Create new company if none exists
                    company = CompanyInfo(
                        name='KodesMind',
                        tagline='Innovative Software Solutions & Digital Transformation',
                        email='info@kodesmind.com',
                        phone='+1 (555) KODES-01',
                        address='123 Innovation Drive, Tech City, TC 12345',
                        about_us='KodesMind is a leading technology company specializing in custom software development, digital transformation, and innovative solutions for modern businesses.',
                        is_active=True
                    )
                    db.session.add(company)
                    db.session.commit()
                    print("✅ New company record created with name 'KodesMind'")

            except Exception as e:
                print(f"Error updating database: {e}")
                db.session.rollback()
                return False

        return True

    if __name__ == '__main__':
        success = update_company_name()
        if success:
            print("✅ Company name update completed successfully!")
        else:
            print("❌ Company name update failed!")

except ImportError as e:
    print(f"Import error: {e}")
    print("Please make sure you're running this from the correct directory with proper Python path")
except Exception as e:
    print(f"Unexpected error: {e}")
