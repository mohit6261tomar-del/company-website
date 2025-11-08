#!/usr/bin/env python3
"""
Script to populate the services table with sample data
"""

import sqlite3
import os
from datetime import datetime

def populate_services():
    """Add sample services to the database"""

    # Sample services data
    services_data = [
        {
            'title': 'Web Development',
            'slug': 'web-development',
            'description': 'Custom web applications built with modern technologies',
            'content': '''We specialize in creating custom web applications using the latest technologies and frameworks. Our team delivers scalable, secure, and user-friendly solutions that drive business growth.

Key features:
• Responsive design for all devices
• Modern frameworks (React, Vue, Angular)
• Backend development (Node.js, Python, PHP)
• Database design and optimization
• API development and integration
• Performance optimization''',
            'icon': 'fas fa-code',
            'image_path': 'img/services/web-dev.jpg',
            'is_featured': True,
            'is_active': True,
            'order_position': 1
        },
        {
            'title': 'Mobile App Development',
            'slug': 'mobile-app-development',
            'description': 'Native and cross-platform mobile applications',
            'content': '''Build powerful mobile applications for iOS and Android platforms. We create native apps for optimal performance and cross-platform solutions for broader reach.

Our mobile development services include:
• Native iOS development (Swift, Objective-C)
• Native Android development (Kotlin, Java)
• Cross-platform solutions (React Native, Flutter)
• App Store optimization
• Push notifications and analytics
• Offline functionality and data sync''',
            'icon': 'fas fa-mobile-alt',
            'image_path': 'img/services/mobile-app.jpg',
            'is_featured': True,
            'is_active': True,
            'order_position': 2
        },
        {
            'title': 'UI/UX Design',
            'slug': 'ui-ux-design',
            'description': 'Beautiful and intuitive user interface design',
            'content': '''Create stunning user interfaces that provide exceptional user experiences. Our design team focuses on usability, accessibility, and visual appeal.

Design services:
• User research and analysis
• Wireframing and prototyping
• Visual design and branding
• Usability testing
• Design systems creation
• Responsive design for all devices''',
            'icon': 'fas fa-palette',
            'image_path': 'img/services/ui-ux.jpg',
            'is_featured': True,
            'is_active': True,
            'order_position': 3
        },
        {
            'title': 'Digital Marketing',
            'slug': 'digital-marketing',
            'description': 'Data-driven digital marketing strategies',
            'content': '''Grow your online presence with our comprehensive digital marketing services. We use data-driven strategies to increase visibility and drive conversions.

Marketing solutions:
• Search engine optimization (SEO)
• Pay-per-click advertising (PPC)
• Social media marketing
• Content marketing
• Email marketing campaigns
• Analytics and reporting''',
            'icon': 'fas fa-chart-line',
            'image_path': 'img/services/digital-marketing.jpg',
            'is_featured': False,
            'is_active': True,
            'order_position': 4
        },
        {
            'title': 'Cloud Solutions',
            'slug': 'cloud-solutions',
            'description': 'Scalable cloud infrastructure and deployment',
            'content': '''Leverage the power of cloud computing for scalable and reliable solutions. We help businesses migrate to and optimize their cloud infrastructure.

Cloud services:
• Cloud migration strategy
• Infrastructure as a Service (IaaS)
• Platform as a Service (PaaS)
• Software as a Service (SaaS)
• DevOps and automation
• Security and compliance''',
            'icon': 'fas fa-cloud',
            'image_path': 'img/services/cloud.jpg',
            'is_featured': False,
            'is_active': True,
            'order_position': 5
        },
        {
            'title': 'Consulting & Strategy',
            'slug': 'consulting-strategy',
            'description': 'Strategic technology consulting and planning',
            'content': '''Get expert guidance on technology strategy and digital transformation. Our consultants help you make informed decisions about your technology investments.

Consulting services:
• Technology assessment
• Digital transformation strategy
• Project planning and management
• Technology roadmap development
• Vendor selection and evaluation
• Training and knowledge transfer''',
            'icon': 'fas fa-lightbulb',
            'image_path': 'img/services/consulting.jpg',
            'is_featured': False,
            'is_active': True,
            'order_position': 6
        }
    ]

    # Connect to database
    db_path = 'instance/site.db'
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Insert sample services
        for service in services_data:
            cursor.execute('''
                INSERT OR REPLACE INTO service
                (title, slug, description, content, icon, image_path, is_featured, is_active, order_position, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                service['title'],
                service['slug'],
                service['description'],
                service['content'],
                service['icon'],
                service['image_path'],
                service['is_featured'],
                service['is_active'],
                service['order_position'],
                datetime.now(),
                datetime.now()
            ))

        conn.commit()
        print(f"✅ Successfully added {len(services_data)} services to the database")

        # Show what was added
        cursor.execute('SELECT COUNT(*) FROM service WHERE is_active = 1')
        active_count = cursor.fetchone()[0]
        print(f"📊 Total active services: {active_count}")

        return True

    except Exception as e:
        print(f"❌ Error adding services: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()

if __name__ == "__main__":
    print("🚀 Populating services table with sample data...")
    populate_services()
    print("✅ Services population complete!")
