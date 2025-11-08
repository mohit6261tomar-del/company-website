#!/usr/bin/env python3

"""
Script to update company name to KodesMind
"""

from app import create_app, db
from app.models import CompanyInfo

def update_company_name():
    """Update the company name to KodesMind"""

    app = create_app()
    with app.app_context():
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

if __name__ == '__main__':
    update_company_name()
