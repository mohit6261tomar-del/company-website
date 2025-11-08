from flask import render_template, request, redirect, url_for, flash, current_app
from app.main import bp
from app.models import CompanyInfo, Service, Portfolio, Blog, Career, ContactMessage, Team, JobApplication
from app.forms import ContactForm, JobApplicationForm
from app import db
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import uuid

@bp.route('/')
def index():
    company = CompanyInfo.query.first()
    services = Service.query.filter_by(is_active=True).limit(6).all()
    featured_portfolio = Portfolio.query.filter_by(is_featured=True).first()
    recent_blogs = Blog.query.filter_by(is_published=True).order_by(Blog.created_at.desc()).limit(3).all()
    team = Team.query.filter_by(is_active=True).order_by(Team.join_date).limit(4).all()
    return render_template('main/index.html', 
                         company=company, 
                         services=services,
                         featured_portfolio=featured_portfolio,
                         recent_blogs=recent_blogs,
                         team=team)

@bp.route('/about')
def about():
    company = CompanyInfo.query.first()
    team = Team.query.filter_by(is_active=True).order_by(Team.join_date).all()
    return render_template('main/about.html', company=company, team=team)

@bp.route('/services')
def services():
    company = CompanyInfo.query.first()
    services = Service.query.filter_by(is_active=True).all()
    return render_template('main/services.html', company=company, services=services)

@bp.route('/portfolio')
def portfolio():
    company = CompanyInfo.query.first()
    portfolios = Portfolio.query.order_by(Portfolio.created_at.desc()).all()
    return render_template('main/portfolio.html', company=company, portfolios=portfolios)

@bp.route('/portfolio/<int:portfolio_id>')
def portfolio_detail(portfolio_id):
    company = CompanyInfo.query.first()
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    return render_template('main/portfolio_detail.html', company=company, portfolio=portfolio)

@bp.route('/blog')
def blog():
    company = CompanyInfo.query.first()
    page = request.args.get('page', 1, type=int)
    posts = Blog.query.filter_by(is_published=True)\
                     .order_by(Blog.created_at.desc())\
                     .paginate(page=page, per_page=5)
    return render_template('main/blog.html', company=company, posts=posts)

@bp.route('/blog/<string:slug>')
def blog_post(slug):
    company = CompanyInfo.query.first()
    post = Blog.query.filter_by(slug=slug, is_published=True).first_or_404()
    return render_template('main/blog_post.html', company=company, post=post)

@bp.route('/careers')
def careers():
    company = CompanyInfo.query.first()
    careers = Career.query.filter_by(is_active=True).order_by(Career.created_at.desc()).all()
    return render_template('main/careers.html', company=company, careers=careers)

@bp.route('/careers/<int:career_id>', methods=['GET', 'POST'])
def career_detail(career_id):
    company = CompanyInfo.query.first()
    career = Career.query.get_or_404(career_id)
    form = JobApplicationForm()
    
    if not career.is_active:
        return redirect(url_for('main.careers'))
    
    if form.validate_on_submit():
        # Handle resume upload
        resume_path = None
        if 'resume' in request.files:
            file = request.files['resume']
            if file and file.filename:
                filename = secure_filename(file.filename)
                if filename:
                    # Create uploads/resumes directory if it doesn't exist
                    upload_folder = os.path.join(current_app.static_folder, 'uploads', 'resumes')
                    os.makedirs(upload_folder, exist_ok=True)
                    
                    # Generate a unique filename
                    unique_filename = f"{uuid.uuid4().hex[:8]}_{filename}"
                    file_path = os.path.join('uploads', 'resumes', unique_filename)
                    full_path = os.path.join(current_app.static_folder, file_path)
                    
                    try:
                        file.save(full_path)
                        resume_path = file_path.replace('\\', '/')
                    except Exception as e:
                        current_app.logger.error(f"Error saving resume: {e}")
                        flash('Error uploading resume. Please try again.', 'error')
        
        # Create job application
        application = JobApplication(
            career_id=career.id,
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            cover_letter=form.cover_letter.data,
            resume_path=resume_path
        )
        
        try:
            db.session.add(application)
            db.session.commit()
            flash('Your application has been submitted successfully! We will review it and get back to you soon.', 'success')
            return redirect(url_for('main.career_detail', career_id=career.id))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error saving job application: {e}")
            flash('An error occurred while submitting your application. Please try again.', 'danger')
        
    return render_template('main/career_detail.html', 
                         company=company, 
                         career=career,
                         form=form)

@bp.route('/contact', methods=['GET', 'POST'])
def contact():
    company = CompanyInfo.query.first()
    form = ContactForm()
    if form.validate_on_submit():
        # Create and save the message
        contact_msg = ContactMessage(
            name=form.name.data,
            email=form.email.data,
            subject=form.subject.data,
            message=form.message.data
        )
        
        try:
            db.session.add(contact_msg)
            db.session.commit()
            flash('Your message has been sent successfully! We will get back to you soon.', 'success')
            return redirect(url_for('main.contact'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error saving contact message: {str(e)}")
            flash('An error occurred while sending your message. Please try again later.', 'danger')
    
    return render_template('main/contact.html', company=company, form=form)

# Error handlers
@bp.app_errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@bp.app_errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500
