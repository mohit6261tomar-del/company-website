from datetime import datetime
from app import db, login_manager, bcrypt
from flask_login import UserMixin
import os

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(60), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    
    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()
    
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

class CompanyInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    tagline = db.Column(db.String(200))
    logo_path = db.Column(db.String(200))
    favicon_path = db.Column(db.String(200))
    about_us = db.Column(db.Text)
    address = db.Column(db.Text)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    
    # Social Media
    facebook_url = db.Column(db.String(200))
    twitter_url = db.Column(db.String(200))
    linkedin_url = db.Column(db.String(200))
    instagram_url = db.Column(db.String(200))
    youtube_url = db.Column(db.String(200))
    
    # SEO
    seo_title = db.Column(db.String(200))
    seo_description = db.Column(db.Text)
    seo_keywords = db.Column(db.String(500))
    
    # Analytics and Tracking
    google_analytics_code = db.Column(db.Text)
    facebook_pixel_code = db.Column(db.Text)
    
    # Custom Code
    custom_css = db.Column(db.Text)
    custom_js = db.Column(db.Text)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Map
    map_embed_code = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"CompanyInfo('{self.name}')"

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic Information
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    skills = db.Column(db.String(200))
    
    # Photo
    photo_path = db.Column(db.String(200))
    
    # Social Media
    linkedin_url = db.Column(db.String(200))
    twitter_url = db.Column(db.String(200))
    facebook_url = db.Column(db.String(200))
    instagram_url = db.Column(db.String(200))
    
    # Display Options
    is_active = db.Column(db.Boolean, default=True)
    featured = db.Column(db.Boolean, default=False)
    order_position = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    join_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f"Team('{self.name}', '{self.position}')"

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text)
    icon = db.Column(db.String(50))
    image_path = db.Column(db.String(200))
    is_featured = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    order_position = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"Service('{self.title}')"

class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    client = db.Column(db.String(100))
    project_date = db.Column(db.Date)
    date_completed = db.Column(db.Date, nullable=True)
    project_url = db.Column(db.String(200))
    is_featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    images = db.relationship('PortfolioImage', backref='portfolio', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"Portfolio('{self.project_name}')"

class PortfolioImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String(200), nullable=False)
    is_primary = db.Column(db.Boolean, default=False)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolio.id'), nullable=False)
    
    def __repr__(self):
        return f"PortfolioImage('{self.image_path}')"

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.Text)
    featured_image = db.Column(db.String(200))
    slug = db.Column(db.String(200), unique=True, nullable=False)
    is_published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', backref=db.backref('blog_posts', lazy=True))
    
    def __repr__(self):
        return f"Blog('{self.title}', '{self.created_at}')"

class Career(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text)
    responsibilities = db.Column(db.Text)
    location = db.Column(db.String(100))
    job_type = db.Column(db.String(50))  # Full-time, Part-time, Contract, etc.
    salary_range = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f"Career('{self.job_title}', '{self.location}')"

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200))
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f"ContactMessage('{self.name}', '{self.email}')"

class JobApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    career_id = db.Column(db.Integer, db.ForeignKey('career.id'), nullable=False)
    career = db.relationship('Career', backref=db.backref('applications', lazy=True))
    
    # Applicant Information
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    cover_letter = db.Column(db.Text, nullable=False)
    
    # Resume File
    resume_path = db.Column(db.String(200))
    
    # Status
    status = db.Column(db.String(20), default='pending')  # pending, reviewed, shortlisted, rejected, hired
    is_reviewed = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"JobApplication('{self.name}', '{self.career.job_title}')"

class PageView(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    page_url = db.Column(db.String(500), nullable=False)
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.Text)
    referrer = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f"PageView('{self.page_url}', '{self.created_at}')"
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
