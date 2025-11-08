from datetime import datetime
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField, TextAreaField, BooleanField, SubmitField, 
    HiddenField, IntegerField, DateTimeField, SelectField, DateField
)
from wtforms.validators import DataRequired, Optional, URL, Email, Length, EqualTo, ValidationError
from app.models import User

class CompanyInfoForm(FlaskForm):
    # Basic Information
    name = StringField('Company Name', validators=[DataRequired()])
    tagline = StringField('Tagline', validators=[DataRequired()])
    favicon = FileField('Favicon', validators=[FileAllowed(['ico', 'png'], 'Favicon must be .ico or .png')])
    about_us = TextAreaField('About Us', validators=[DataRequired()])
    address = TextAreaField('Address')
    email = StringField('Contact Email', validators=[DataRequired()])
    phone = StringField('Phone Number')
    
    # Social Media
    facebook_url = StringField('Facebook URL', validators=[Optional(), URL()])
    twitter_url = StringField('Twitter URL', validators=[Optional(), URL()])
    linkedin_url = StringField('LinkedIn URL', validators=[Optional(), URL()])
    instagram_url = StringField('Instagram URL', validators=[Optional(), URL()])
    youtube_url = StringField('YouTube URL', validators=[Optional(), URL()])
    
    # SEO
    seo_title = StringField('SEO Title', validators=[Optional()])
    seo_description = TextAreaField('Meta Description', validators=[Optional()])
    seo_keywords = StringField('Meta Keywords', validators=[Optional()])
    
    # Analytics & Tracking
    google_analytics_code = TextAreaField('Google Analytics Code', validators=[Optional()])
    facebook_pixel_code = TextAreaField('Facebook Pixel Code', validators=[Optional()])
    
    # Custom Code
    custom_css = TextAreaField('Custom CSS', validators=[Optional()])
    custom_js = TextAreaField('Custom JavaScript', validators=[Optional()])
    
    # Map
    map_embed_code = TextAreaField('Map Embed Code', validators=[Optional()])
    
    # Status
    is_active = BooleanField('Active', default=True)
    
    submit = SubmitField('Save Changes')

class TeamMemberForm(FlaskForm):
    # Basic Information
    name = StringField('Full Name', validators=[DataRequired()])
    position = StringField('Position', validators=[DataRequired()])
    bio = TextAreaField('Biography')
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone')
    skills = StringField('Skills')
    
    # Photo
    photo = FileField('Profile Photo', validators=[
        FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Only image files are allowed')
    ])
    photo_path = HiddenField()
    
    # Social Media
    linkedin_url = StringField('LinkedIn URL', validators=[Optional(), URL()])
    twitter_url = StringField('Twitter URL', validators=[Optional(), URL()])
    facebook_url = StringField('Facebook URL', validators=[Optional(), URL()])
    instagram_url = StringField('Instagram URL', validators=[Optional(), URL()])
    
    # Display Options
    is_active = BooleanField('Active', default=True)
    featured = BooleanField('Featured on Homepage', default=False)
    order_position = IntegerField('Display Order', default=0, validators=[Optional()])
    
    submit = SubmitField('Save Team Member')

class ServiceForm(FlaskForm):
    # Basic Information
    title = StringField('Service Title', validators=[DataRequired()])
    slug = StringField('URL Slug', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Short Description', validators=[DataRequired(), Length(max=300)], 
                              render_kw={"rows": 3})
    content = TextAreaField('Detailed Content', render_kw={"rows": 5, "class": "summernote"})
    
    # Media
    icon = StringField('Icon Class (e.g., fas fa-code)', 
                      description='Use Font Awesome or other icon library classes')
    image = FileField('Service Image', 
                     validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')])
    
    # Display Options
    is_featured = BooleanField('Feature this service on homepage', default=False)
    is_active = BooleanField('Active', default=True)
    order_position = IntegerField('Display Order', default=0, 
                                description='Lower numbers appear first')
    
    submit = SubmitField('Save Service')
    
    def validate_slug(self, field):
        from app.models import Service
        from flask import request
        
        # Check if slug is being updated
        if 'id' in request.form and request.form['id']:
            service = Service.query.get(request.form['id'])
            if service and service.slug == field.data:
                return
        
        # Check if slug is unique
        if Service.query.filter_by(slug=field.data).first():
            from wtforms.validators import ValidationError
            raise ValidationError('This slug is already in use. Please choose a different one.')

class PortfolioForm(FlaskForm):
    project_name = StringField('Project Name', validators=[DataRequired()])
    description = TextAreaField('Project Description', validators=[DataRequired()])
    client = StringField('Client')
    project_date = DateField('Project Date', format='%Y-%m-%d', validators=[Optional()])
    project_url = StringField('Project URL', validators=[Optional(), URL()])
    is_featured = BooleanField('Feature this project on the homepage')
    images = FileField('Project Images', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')])
    submit = SubmitField('Save Project')

class BlogPostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    slug = StringField('URL Slug', validators=[DataRequired(), Length(max=200)])
    excerpt = TextAreaField('Excerpt', validators=[Length(max=500)])
    content = TextAreaField('Content', validators=[DataRequired()])
    featured_image = FileField('Featured Image', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')])
    is_published = BooleanField('Publish this post')
    submit = SubmitField('Publish Post')

class CareerForm(FlaskForm):
    job_title = StringField('Job Title', validators=[DataRequired()])
    description = TextAreaField('Job Description', validators=[DataRequired()])
    requirements = TextAreaField('Requirements', validators=[DataRequired()])
    responsibilities = TextAreaField('Responsibilities', validators=[DataRequired()])
    location = StringField('Location')
    job_type = SelectField('Job Type', choices=[
        ('full-time', 'Full Time'),
        ('part-time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('freelance', 'Freelance')
    ])
    salary_range = StringField('Salary Range')
    is_active = BooleanField('This position is currently open', default=True)
    submit = SubmitField('Post Job')

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = StringField('Password', validators=[
        Optional(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    confirm_password = StringField('Confirm Password', validators=[
        EqualTo('password', message='Passwords must match')
    ])
    is_admin = BooleanField('Is Admin')
    is_active = BooleanField('Is Active', default=True)
    submit = SubmitField('Save User')
    
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.user = None
    
    def validate_username(self, username):
        if self.user and self.user.username == username.data:
            return
        if User.query.filter_by(username=username.data).first() is not None:
            raise ValidationError('Please use a different username.')
    
    def validate_email(self, email):
        if self.user and self.user.email == email.data:
            return
        if User.query.filter_by(email=email.data).first() is not None:
            raise ValidationError('Please use a different email address.')
