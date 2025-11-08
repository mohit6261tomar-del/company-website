#!/usr/bin/env python3

"""
Script to verify company name has been updated to KodesMind
"""

from app import create_app, db
from app.models import CompanyInfo

def check_company_name():
    """Check the current company name"""

    app = create_app()
    with app.app_context():
        company = CompanyInfo.query.first()

        if company:
            print(f"Company name: '{company.name}'")
            print(f"Company tagline: '{company.tagline}'")
            print(f"Company email: '{company.email}'")
        else:
            print("No company record found")

if __name__ == '__main__':
    check_company_name()
