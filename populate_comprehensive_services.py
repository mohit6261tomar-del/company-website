from app import create_app, db
from app.models import Service
from datetime import datetime

def populate_services():
    """Populate the database with comprehensive service categories and services"""

    app = create_app()
    with app.app_context():
        # Clear existing services
        Service.query.delete()
        db.session.commit()

        # Service categories and their detailed services
        service_data = {
            "Software Development Services": {
                "icon": "fas fa-laptop-code",
                "description": "End-to-end software solutions tailored to client needs.",
                "services": {
                    "Custom Software Development": "Tailored software solutions designed specifically for your business needs and requirements.",
                    "Web Application Development": "Full-stack web applications using React, Angular, Node.js, .NET, Java, and modern frameworks.",
                    "Mobile App Development": "Native iOS/Android and cross-platform applications using Flutter and React Native.",
                    "SaaS Product Development": "Cloud-based subscription software solutions with scalable architecture.",
                    "API Development & Integration": "REST and GraphQL APIs with seamless third-party integrations."
                }
            },
            "Cloud & Infrastructure Services": {
                "icon": "fas fa-cloud",
                "description": "Scalable and secure cloud solutions for modern businesses.",
                "services": {
                    "Cloud Migration & Modernization": "Seamless transition to AWS, Azure, or GCP with minimal downtime and maximum efficiency.",
                    "DevOps Services": "CI/CD pipelines, Docker, Kubernetes, and infrastructure automation.",
                    "Cloud Architecture Design": "Scalable and secure cloud environments with high availability.",
                    "Server Management & Monitoring": "24/7 server monitoring, maintenance, and performance optimization.",
                    "Backup & Disaster Recovery Solutions": "Comprehensive data protection and business continuity strategies."
                }
            },
            "Cybersecurity Services": {
                "icon": "fas fa-shield-alt",
                "description": "Advanced security solutions to protect your digital assets.",
                "services": {
                    "Vulnerability Assessment & Penetration Testing": "Comprehensive security audits and penetration testing services.",
                    "Network Security Management": "Advanced firewall, intrusion detection, and threat prevention systems.",
                    "Data Protection & Encryption": "End-to-end data encryption and secure data transmission protocols.",
                    "Identity & Access Management": "Multi-factor authentication and role-based access control systems.",
                    "Security Compliance": "ISO 27001, GDPR, HIPAA, and industry-specific compliance frameworks."
                }
            },
            "AI, Data & Analytics": {
                "icon": "fas fa-brain",
                "description": "Data-driven insights and intelligent automation solutions.",
                "services": {
                    "Data Warehousing & ETL Solutions": "Scalable data lakes and efficient ETL pipelines for data processing.",
                    "Business Intelligence Dashboards": "Interactive dashboards and reporting solutions for data visualization.",
                    "Machine Learning Model Development": "Custom ML models for prediction, classification, and automation.",
                    "Generative AI Integration": "Chatbots, content generation, and AI-powered applications.",
                    "Predictive Analytics": "Advanced analytics for forecasting and trend analysis."
                }
            },
            "Web & Digital Services": {
                "icon": "fas fa-globe",
                "description": "Comprehensive digital solutions for online presence.",
                "services": {
                    "Website Design & Development": "Responsive websites with modern design and optimal user experience.",
                    "E-Commerce Development": "Complete e-commerce solutions using Shopify, WooCommerce, and Magento.",
                    "SEO & Digital Marketing": "Search engine optimization and comprehensive digital marketing strategies.",
                    "UI/UX Design & Branding": "User-centered design and cohesive brand identity development.",
                    "Content Management Systems": "WordPress, Drupal, Strapi, and custom CMS solutions."
                }
            },
            "IT Consulting & Support": {
                "icon": "fas fa-headset",
                "description": "Strategic IT guidance and comprehensive support services.",
                "services": {
                    "IT Strategy & Roadmap Planning": "Comprehensive technology strategy and digital transformation roadmaps.",
                    "Technology Stack Evaluation": "Assessment and recommendation of optimal technology solutions.",
                    "Software Project Rescue & Audit": "Project recovery, code review, and performance optimization.",
                    "IT Helpdesk & Remote Support": "24/7 technical support and remote assistance services.",
                    "Managed IT Services": "Complete IT infrastructure management and maintenance."
                }
            },
            "Enterprise Solutions": {
                "icon": "fas fa-building",
                "description": "Large-scale solutions for complex business operations.",
                "services": {
                    "ERP & CRM Implementation": "SAP, Salesforce, Odoo, and custom enterprise resource planning.",
                    "HRMS, Payroll, and Inventory Systems": "Human resource management and inventory tracking solutions.",
                    "Workflow Automation": "Business process automation and workflow optimization.",
                    "Legacy System Modernization": "Migration from legacy systems to modern cloud platforms."
                }
            },
            "Integration & Automation": {
                "icon": "fas fa-robot",
                "description": "Seamless integration and intelligent automation solutions.",
                "services": {
                    "System Integration Services": "Enterprise application integration and middleware solutions.",
                    "Robotic Process Automation": "RPA implementation for repetitive task automation.",
                    "API Gateway & Microservices": "API management and microservices architecture design.",
                    "IoT System Integration": "Internet of Things platform integration and device management."
                }
            },
            "Emerging Technologies": {
                "icon": "fas fa-atom",
                "description": "Cutting-edge technology solutions for future-ready businesses.",
                "services": {
                    "Blockchain Development": "Smart contracts, DeFi applications, and NFT platform development.",
                    "Internet of Things": "IoT device development, edge computing, and sensor networks.",
                    "AR/VR Application Development": "Augmented and virtual reality applications for various industries.",
                    "Metaverse & Digital Twins": "Metaverse development and digital twin simulation solutions."
                }
            },
            "Outsourcing & Staffing": {
                "icon": "fas fa-users",
                "description": "Flexible staffing and development team solutions.",
                "services": {
                    "Dedicated Development Teams": "Full-time dedicated teams for long-term projects.",
                    "IT Staff Augmentation": "Skilled professionals to supplement your existing team.",
                    "Project-Based Outsourcing": "Complete project outsourcing with defined deliverables.",
                    "Remote Developer Hiring": "Global talent acquisition and remote team management."
                }
            }
        }

        # Add services to database
        for category_name, category_data in service_data.items():
            # Create category service
            category_slug = category_name.lower().replace(' ', '-').replace('&', 'and').replace(',', '').replace('services', 'services')
            category_service = Service(
                title=category_name,
                slug=category_slug,
                description=category_data["description"],
                content="<h3>Our Services Include:</h3><ul>" +
                        "".join([f"<li><strong>{service_name}</strong>: {description}</li>"
                                for service_name, description in category_data["services"].items()]) + "</ul>",
                icon=category_data["icon"],
                is_featured=True,
                is_active=True,
                order_position=0
            )
            db.session.add(category_service)

            # Add individual services
            for service_name, service_description in category_data["services"].items():
                service_slug = f"{category_slug}-{service_name.lower().replace(' ', '-').replace('&', 'and').replace(',', '').replace('(', '').replace(')', '').replace('/', '-')}"
                service = Service(
                    title=service_name,
                    slug=service_slug,
                    description=service_description,
                    content=f"<p>{service_description}</p><p>Contact us to learn more about our {service_name} services.</p>",
                    icon="fas fa-check-circle",
                    is_featured=False,
                    is_active=True,
                    order_position=0
                )
                db.session.add(service)

        db.session.commit()
        print(f"✅ Successfully added {len(service_data)} service categories with individual services!")

        # Display summary
        total_services = Service.query.count()
        featured_services = Service.query.filter_by(is_featured=True).count()
        print(f"📊 Total services in database: {total_services}")
        print(f"⭐ Featured services: {featured_services}")

if __name__ == "__main__":
    populate_services()
