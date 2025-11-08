import random
from datetime import datetime, timedelta
from app import create_app, db
from app.models import BlogCategory, BlogPost, User, BlogTag

app = create_app()

with app.app_context():
    # Get or create user
    admin = User.query.first()
    if not admin:
        admin = User(email='admin@example.com', username='admin', is_admin=True)
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
    
    print(f"Using user: {admin.username} (ID: {admin.id})")
    
    # Categories with post counts
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
    
    # Create categories
    print("\nCreating categories...")
    category_objects = {}
    for name, count in categories_data:
        slug = name.lower().replace(' ', '-')
        category = BlogCategory.query.filter_by(slug=slug).first()
        if not category:
            category = BlogCategory(
                name=name,
                slug=slug,
                description=f"Articles about {name}",
                is_active=True
            )
            db.session.add(category)
            print(f"  Created: {name}")
        else:
            print(f"  Exists: {name}")
        category_objects[name] = category
    
    db.session.commit()
    
    # Create tags
    print("\nCreating tags...")
    tag_names = ['tutorial', 'guide', 'tips', 'best-practices', 'case-study', 'trends', 'innovation', 'strategy', 'tools', 'resources']
    tag_objects = {}
    for tag_name in tag_names:
        tag = BlogTag.query.filter_by(slug=tag_name).first()
        if not tag:
            tag = BlogTag(name=tag_name.title(), slug=tag_name)
            db.session.add(tag)
        tag_objects[tag_name] = tag
    
    db.session.commit()
    
    # Create blog posts
    print("\nCreating blog posts...")
    total_posts = 0
    
    for category_name, post_count in categories_data:
        category = category_objects[category_name]
        print(f"\nCreating {post_count} posts for {category_name}...")
        
        for i in range(post_count):
            title = f"{category_name} Article {i+1}: Best Practices for {datetime.now().year}"
            slug = f"{category.slug}-article-{i+1}-{total_posts}"
            
            content = f"<p>This is a comprehensive article about {title.lower()}.</p><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>"
            excerpt = f"Learn about {category_name.lower()} best practices and insights."
            
            # Create post
            post = BlogPost(
                title=title,
                slug=slug,
                excerpt=excerpt,
                content=content,
                is_published=True,
                is_featured=(i < 2),
                view_count=random.randint(50, 1000),
                author_id=admin.id,
                category_id=category.id
            )
            
            # Add random tags
            post_tags = random.sample(list(tag_objects.values()), k=random.randint(1, 3))
            post.tags.extend(post_tags)
            
            db.session.add(post)
            total_posts += 1
            
            if total_posts % 20 == 0:
                db.session.commit()
                print(f"  Created {total_posts} posts...")
    
    db.session.commit()
    
    print(f"\n✅ Successfully created {total_posts} blog posts!")
    print("\nSummary:")
    for name, expected_count in categories_data:
        category = category_objects[name]
        actual_count = category.posts.count()
        print(f"  {name}: {actual_count} posts")
