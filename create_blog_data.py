import os
import random
from datetime import datetime, timedelta
from app import create_app, db
from app.models import BlogCategory, BlogPost, User, BlogTag

def create_blog_data_simple():
    """Create blog categories and posts with simple data"""
    app = create_app()

    with app.app_context():
        try:
            # Check if admin user exists
            admin = User.query.filter_by(is_admin=True).first()
            if not admin:
                print("No admin user found. Using first available user or creating one...")
                admin = User.query.first()
                if not admin:
                    # Create a simple admin user
                    from app import bcrypt
                    admin = User(
                        email='admin@example.com',
                        username='admin',
                        is_admin=True
                    )
                    admin.set_password('admin123')
                    db.session.add(admin)
                    db.session.commit()
                    print(f"Created admin user: {admin.email}")
                else:
                    print(f"Using existing user: {admin.email}")

            # Define categories with their post counts
            categories_data = [
                ("Technology", 25),
                ("Business", 18),
                ("Design", 15),
                ("Development", 22),
                ("Marketing", 12),
                ("Digital Transformation", 8),
                ("Productivity", 14),
                ("Remote Work", 10)
            ]

            # Create categories if they don't exist
            category_objects = {}
            print("Creating blog categories...")

            for name, count in categories_data:
                slug = name.lower().replace(' ', '-').replace('digital-transformation', 'digital-transformation')
                category = BlogCategory.query.filter_by(slug=slug).first()

                if not category:
                    category = BlogCategory(
                        name=name,
                        slug=slug,
                        description=f"Articles and insights about {name}",
                        is_active=True
                    )
                    db.session.add(category)
                    print(f"Created category: {name}")
                else:
                    print(f"Category already exists: {name}")

                category_objects[name] = category

            # Create some default tags if they don't exist
            print("Creating default tags...")
            default_tags = [
                'tutorial', 'guide', 'tips', 'best-practices', 'case-study',
                'trends', 'innovation', 'strategy', 'tools', 'resources'
            ]

            tag_objects = {}
            for tag_name in default_tags:
                tag = BlogTag.query.filter_by(slug=tag_name).first()
                if not tag:
                    tag = BlogTag(name=tag_name.title(), slug=tag_name)
                    db.session.add(tag)
                tag_objects[tag_name] = tag

            db.session.commit()

            # Sample blog post templates for each category
            post_templates = {
                "Technology": [
                    "The Future of Artificial Intelligence in {year}",
                    "How {technology} is Revolutionizing Our World",
                    "Top {number} Technology Trends to Watch in {year}",
                    "Understanding {technology}: A Comprehensive Guide",
                    "The Impact of {technology} on Modern Business"
                ],
                "Business": [
                    "Building a Successful Business Strategy in {year}",
                    "Essential Leadership Skills for Modern Entrepreneurs",
                    "How to Scale Your Business Effectively",
                    "The Art of Negotiation in Business",
                    "Digital Marketing Strategies for Small Businesses"
                ],
                "Design": [
                    "Principles of Modern Web Design",
                    "The Psychology of Color in Branding",
                    "Creating User-Centered Design Experiences",
                    "Typography Trends That Define {year}",
                    "Mobile-First Design: Best Practices"
                ],
                "Development": [
                    "Getting Started with {framework} Development",
                    "Best Practices for Clean Code Architecture",
                    "Building Scalable Web Applications",
                    "Debugging Techniques Every Developer Should Know",
                    "Version Control Strategies for Teams"
                ],
                "Marketing": [
                    "Content Marketing Strategies That Drive Results",
                    "Social Media Marketing in the Digital Age",
                    "SEO Best Practices for {year}",
                    "Email Marketing Campaigns That Convert",
                    "Influencer Marketing: Trends and Tips"
                ],
                "Digital Transformation": [
                    "Digital Transformation: A Roadmap for Success",
                    "Cloud Computing and Business Agility",
                    "Data Analytics in Digital Transformation",
                    "AI and Machine Learning in Business",
                    "The Future of Work in a Digital World"
                ],
                "Productivity": [
                    "Time Management Techniques for Busy Professionals",
                    "Building Better Habits for Increased Productivity",
                    "Tools and Apps That Boost Workplace Efficiency",
                    "The Power of Focus and Concentration",
                    "Work-Life Balance in the Modern Workplace"
                ],
                "Remote Work": [
                    "Building a Successful Remote Work Culture",
                    "Tools for Effective Remote Collaboration",
                    "Managing Remote Teams: Best Practices",
                    "The Future of Remote Work Post-Pandemic",
                    "Creating a Productive Home Office Environment"
                ]
            }

            # Create blog posts for each category
            print("Creating blog posts...")
            total_posts = 0

            for category_name, post_count in categories_data:
                category = category_objects[category_name]
                templates = post_templates.get(category_name, ["Sample Post for {category}"])

                print(f"Creating {post_count} posts for category: {category_name}")

                for i in range(post_count):
                    # Select a random template
                    template = templates[i % len(templates)]

                    # Fill in the template
                    title = template.format(
                        year=str(datetime.now().year),
                        technology=["AI", "Blockchain", "IoT", "Cloud Computing", "Machine Learning"][i % 5],
                        number=str(i + 1),
                        framework=["React", "Vue.js", "Django", "Laravel", "Express.js"][i % 5],
                        category=category_name
                    )

                    # Create slug from title
                    slug = title.lower().replace(' ', '-').replace(':', '').replace(',', '')

                    # Generate content (simple paragraphs)
                    content = f"""
                    <p>This is a sample blog post about {title.lower()}. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>

                    <p>Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.</p>

                    <h3>Key Points</h3>
                    <ul>
                        <li>Point one about {category_name.lower()}</li>
                        <li>Point two with important insights</li>
                        <li>Point three for comprehensive understanding</li>
                    </ul>

                    <p>Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum. This concludes our discussion on {title.lower()}.</p>
                    """

                    # Generate excerpt
                    excerpt = f"This article explores {title.lower()}, providing insights and practical information for {category_name.lower()} professionals and enthusiasts."

                    # Random published date within last 2 years
                    published_date = datetime.now() - timedelta(days=random.randint(1, 730))

                    # Create blog post
                    blog_post = BlogPost(
                        title=title,
                        slug=slug,
                        excerpt=excerpt,
                        content=content,
                        featured_image=None,
                        is_published=True,
                        is_featured=i < 2,  # First 2 posts are featured
                        view_count=random.randint(50, 1000),
                        created_at=published_date,
                        updated_at=published_date,
                        published_at=published_date,
                        author_id=admin.id,
                        category_id=category.id
                    )

                    # Assign 1-3 random tags
                    post_tags = random.sample(list(tag_objects.values()),
                                            k=random.randint(1, min(3, len(tag_objects))))
                    blog_post.tags.extend(post_tags)

                    db.session.add(blog_post)
                    total_posts += 1

                    if total_posts % 10 == 0:
                        print(f"Created {total_posts} posts so far...")
                        db.session.commit()

            # Final commit
            db.session.commit()
            print(f"Successfully created {total_posts} blog posts across {len(categories_data)} categories!")
            print("Blog data creation completed.")

            # Print summary
            print("\nSummary:")
            for name, count in categories_data:
                category = category_objects[name]
                actual_count = category.posts.count()
                print(f"  {name}: {actual_count} posts")

        except Exception as e:
            print(f"Error creating blog data: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()

if __name__ == "__main__":
    create_blog_data_simple()
