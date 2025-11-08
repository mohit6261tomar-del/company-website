import random
import os
from faker import Faker
from datetime import datetime, timedelta
from app import create_app, db
from app.models import BlogCategory, BlogPost, User, BlogTag

def create_blog_data():
    """Create blog categories and posts with the specified counts"""
    app = create_app(os.getenv('FLASK_CONFIG') or 'default')

    with app.app_context():
        # Initialize Faker
        fake = Faker()

        # Get or create admin user
        admin = User.query.filter_by(email=app.config.get('ADMIN_EMAIL')).first()
        if not admin:
            print("Admin user not found. Please ensure an admin user exists.")
            return

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
        print("Creating/Checking blog categories...")

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

        # Create blog posts for each category
        print("Creating blog posts...")
        total_posts = 0

        for category_name, post_count in categories_data:
            category = category_objects[category_name]
            print(f"Creating {post_count} posts for category: {category_name}")

            for i in range(post_count):
                # Generate fake post data
                title = fake.sentence(nb_words=6, variable_nb_words=True)
                # Remove the trailing period from the title
                title = title[:-1] if title.endswith('.') else title

                # Create slug from title
                slug = title.lower().replace(' ', '-').replace('?', '').replace('!', '')

                # Generate content
                paragraphs = fake.paragraphs(nb=random.randint(4, 8))
                content = '\n\n'.join(paragraphs)

                # Generate excerpt
                excerpt = fake.paragraph(nb_sentences=2)

                # Random published date within last 2 years
                published_date = fake.date_time_between(
                    start_date='-2y',
                    end_date='now'
                )

                # Create blog post
                blog_post = BlogPost(
                    title=title,
                    slug=slug,
                    excerpt=excerpt,
                    content=content,
                    featured_image=None,  # No featured images for now
                    is_published=True,
                    is_featured=random.choice([True, False]) if random.random() > 0.7 else False,
                    view_count=random.randint(10, 1000),
                    created_at=published_date,
                    updated_at=published_date,
                    published_at=published_date,
                    author_id=admin.id,
                    category_id=category.id
                )

                # Assign random tags (1-3 tags per post)
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

if __name__ == "__main__":
    create_blog_data()
