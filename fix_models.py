# Script to fix models.py by removing null bytes
with open('c:\\Users\\pc\\Downloads\\COMPANY WEBSITE\\app\\models.py', 'rb') as f:
    content = f.read()

# Find where the corruption starts (around line 204)
lines = content.split(b'\n')
print(f'Total lines: {len(lines)}')

# Keep only the clean lines (1-203)
clean_lines = lines[:203]

# Add the clean blog models
blog_models = b'''
# Blog models

class BlogCategory(db.Model):
    """Blog post categories"""
    __tablename__ = 'blog_categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    slug = db.Column(db.String(64), unique=True, index=True)
    description = db.Column(db.Text)
    posts = db.relationship('BlogPost', backref='category', lazy='dynamic')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<BlogCategory {self.name}>'

class BlogPost(db.Model):
    """Blog posts model"""
    __tablename__ = 'blog_posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, index=True)
    excerpt = db.Column(db.Text)
    content = db.Column(db.Text, nullable=False)
    featured_image = db.Column(db.String(255))
    is_published = db.Column(db.Boolean, default=False)
    is_featured = db.Column(db.Boolean, default=False)
    view_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = db.Column(db.DateTime)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('blog_categories.id'))
    comments = db.relationship('BlogComment', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    tags = db.relationship('BlogTag', secondary='blog_post_tags', backref=db.backref('posts', lazy='dynamic'))

    def __repr__(self):
        return f'<BlogPost {self.title}>'

class BlogTag(db.Model):
    """Tags for blog posts"""
    __tablename__ = 'blog_tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    slug = db.Column(db.String(64), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<BlogTag {self.name}>'

# Association table for many-to-many relationship between BlogPost and BlogTag
blog_post_tags = db.Table('blog_post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('blog_posts.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('blog_tags.id'), primary_key=True)
)

class BlogComment(db.Model):
    """Comments on blog posts"""
    __tablename__ = 'blog_comments'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_approved = db.Column(db.Boolean, default=False)
    author_name = db.Column(db.String(64))
    author_email = db.Column(db.String(120))
    post_id = db.Column(db.Integer, db.ForeignKey('blog_posts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<BlogComment by {self.author_name or "Anonymous"}>'
'''

# Combine clean content
final_content = b'\n'.join(clean_lines) + blog_models

# Write the clean file
with open('c:\\Users\\pc\\Downloads\\COMPANY WEBSITE\\app\\models.py', 'wb') as f:
    f.write(final_content)

print(f'✅ File cleaned! Wrote {len(final_content)} bytes')
print(f'✅ Removed corrupted lines and added clean blog models')

# Verify no null bytes
with open('c:\\Users\\pc\\Downloads\\COMPANY WEBSITE\\app\\models.py', 'rb') as f:
    verify_content = f.read()
    null_count = verify_content.count(b'\x00')
    print(f'✅ Null bytes in file: {null_count}')
