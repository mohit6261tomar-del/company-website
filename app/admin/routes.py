import os
import uuid
from datetime import datetime, timedelta
from wtforms.validators import Optional, Length
from flask import render_template, redirect, url_for, flash, request, current_app, abort, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy import func, desc
from app import db
from app.admin import bp
from app.models import User, CompanyInfo, Team, Service, Portfolio, PortfolioImage, Blog, Career, ContactMessage, PageView, JobApplication
from app.admin.forms import (
    CompanyInfoForm, TeamMemberForm, ServiceForm, 
    PortfolioForm, BlogPostForm, CareerForm, UserForm
)
from app.utils import admin_required

def allowed_file(filename, allowed_extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_file(file, folder):
    if file and allowed_file(file.filename, {'png', 'jpg', 'jpeg', 'gif'}):
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.static_folder, 'uploads', folder, filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        file.save(file_path)
        return f'uploads/{folder}/{filename}'
    return None

@bp.before_request
@login_required
def require_login():
    if not current_user.is_authenticated or not current_user.is_admin:
        return redirect(url_for('auth.login'))

@bp.route('/')
@login_required
@admin_required
def dashboard():
    # Calculate date ranges for statistics
    now = datetime.utcnow()
    last_month = now - timedelta(days=30)
    two_months_ago = now - timedelta(days=60)
    
    # Total Visitors
    total_visitors = PageView.query.count()
    prev_month_visitors = PageView.query.filter(PageView.created_at < last_month, 
                                             PageView.created_at > two_months_ago).count()
    current_month_visitors = PageView.query.filter(PageView.created_at >= last_month).count()
    visitor_change = ((current_month_visitors - prev_month_visitors) / prev_month_visitors * 100) if prev_month_visitors else 0
    
    # Total Revenue (placeholder - replace with actual revenue logic)
    total_revenue = 48597  # This should be replaced with actual revenue calculation
    revenue_change = 8.2  # This should be calculated based on your revenue data
    
    # Active Projects
    active_projects = Portfolio.query.filter(
        Portfolio.date_completed.is_(None) | 
        (Portfolio.date_completed > now)
    ).count()
    
    # Pending Requests (contact messages not read)
    pending_requests = ContactMessage.query.filter_by(is_read=False).count()
    
    # Calculate changes for other stats
    prev_month_requests = ContactMessage.query.filter(
        ContactMessage.created_at < last_month,
        ContactMessage.created_at > two_months_ago,
        ContactMessage.is_read == False
    ).count()
    requests_change = ((pending_requests - prev_month_requests) / prev_month_requests * 100) if prev_month_requests else 0
    
    # Prepare stats dictionary
    stats = {
        'services': Service.query.count(),
        'portfolio': Portfolio.query.count(),
        'blog_posts': Blog.query.count(),
        'careers': Career.query.count(),
        'team_members': Team.query.count(),
        'unread_messages': pending_requests,
        'total_visitors': total_visitors,
        'active_users': User.query.filter(User.last_seen > (now - timedelta(minutes=30))).count(),
        'statistics': {
            'visitors': {
                'total': total_visitors,
                'change': visitor_change,
                'is_positive': visitor_change >= 0
            },
            'revenue': {
                'total': total_revenue,
                'change': revenue_change,
                'is_positive': revenue_change >= 0
            },
            'projects': {
                'total': active_projects,
                'change': 5.3,  # This should be calculated based on your project data
                'is_positive': True
            },
            'requests': {
                'total': pending_requests,
                'change': requests_change,
                'is_positive': requests_change <= 0  # Fewer pending requests is better
            }
        }
    }
    
    # Recent activities
    recent_activities = []
    
    # Recent blog posts
    recent_posts = Blog.query.order_by(Blog.created_at.desc()).limit(5).all()
    
    # Recent projects
    recent_projects = Portfolio.query.order_by(Portfolio.date_completed.desc()).limit(5).all()
    
    # Recent messages
    recent_messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).limit(5).all()
    
    # Recent user activities (simplified example)
    recent_activities = [
        {
            'title': 'New Blog Post',
            'description': 'A new blog post was published',
            'time': 'Just now',
            'icon': 'fa-newspaper',
            'type': 'info'
        },
        {
            'title': 'Portfolio Updated',
            'description': 'A new project was added to the portfolio',
            'time': '2 hours ago',
            'icon': 'fa-briefcase',
            'type': 'success'
        },
        {
            'title': 'New Message',
            'description': 'You have a new contact message',
            'time': '5 hours ago',
            'icon': 'fa-envelope',
            'type': 'warning'
        }
    ]
    
    return render_template(
        'admin/dashboard.html',
        stats=stats,
        recent_posts=recent_posts,
        recent_projects=recent_projects,
        recent_messages=recent_messages,
        recent_activities=recent_activities,
        now=datetime.utcnow()
    )

# Team Management Routes
@bp.route('/team')
@login_required
@admin_required
def team():
    team_members = Team.query.order_by(Team.order_position.asc(), Team.name.asc()).all()
    return render_template('admin/team.html', team_members=team_members, title='Team Management')

@bp.route('/team/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_team_member():
    form = TeamMemberForm()
    if form.validate_on_submit():
        member = Team()
        form.populate_obj(member)
        
        # Handle photo upload
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename:  # Check if file exists and has a filename
                filename = secure_filename(file.filename)
                if filename:  # Ensure filename is not empty
                    # Create uploads/team directory if it doesn't exist
                    upload_folder = os.path.join(current_app.static_folder, 'uploads', 'team')
                    os.makedirs(upload_folder, exist_ok=True)
                    
                    # Generate a unique filename
                    unique_filename = f"{uuid.uuid4().hex[:8]}_{filename}"
                    file_path = os.path.join('uploads', 'team', unique_filename)
                    full_path = os.path.join(current_app.static_folder, file_path)
                    
                    try:
                        file.save(full_path)
                        member.photo_path = file_path.replace('\\', '/')
                    except Exception as e:
                        current_app.logger.error(f"Error saving team member photo: {e}")
                        flash('Error saving team member photo.', 'error')
        
        try:
            db.session.add(member)
            db.session.commit()
            flash('Team member added successfully!', 'success')
            
            # Check if save_and_add button was clicked
            if 'save_and_add' in request.form:
                return redirect(url_for('admin.add_team_member'))
            else:
                return redirect(url_for('admin.team'))
                
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error adding team member: {e}")
            flash('An error occurred while adding the team member.', 'error')
    
    return render_template('admin/team_form.html', form=form, title='Add Team Member')

@bp.route('/team/<int:member_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_team_member(member_id):
    member = Team.query.get_or_404(member_id)
    form = TeamMemberForm(obj=member)
    
    if form.validate_on_submit():
        # Handle photo upload
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename:  # Check if file exists and has a filename
                # Delete old photo if exists
                if member.photo_path and os.path.exists(os.path.join(current_app.static_folder, member.photo_path)):
                    try:
                        os.remove(os.path.join(current_app.static_folder, member.photo_path))
                    except Exception as e:
                        current_app.logger.error(f"Error deleting team member photo: {e}")
                
                # Save new photo
                filename = secure_filename(file.filename)
                if filename:  # Ensure filename is not empty
                    upload_folder = os.path.join(current_app.static_folder, 'uploads', 'team')
                    os.makedirs(upload_folder, exist_ok=True)
                    
                    unique_filename = f"{uuid.uuid4().hex[:8]}_{filename}"
                    file_path = os.path.join('uploads', 'team', unique_filename)
                    full_path = os.path.join(current_app.static_folder, file_path)
                    
                    try:
                        file.save(full_path)
                        member.photo_path = file_path.replace('\\', '/')
                    except Exception as e:
                        current_app.logger.error(f"Error saving team member photo: {e}")
                        flash('Error saving team member photo.', 'error')
        
        try:
            form.populate_obj(member)
            db.session.commit()
            flash('Team member updated successfully!', 'success')
            return redirect(url_for('admin.team'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating team member: {e}")
            flash('An error occurred while updating the team member.', 'error')
    
    return render_template('admin/team_form.html', form=form, member=member, title='Edit Team Member')

@bp.route('/team/<int:member_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_team_member(member_id):
    member = Team.query.get_or_404(member_id)
    
    try:
        # Delete photo if exists
        if member.photo_path and os.path.exists(os.path.join(current_app.static_folder, member.photo_path)):
            try:
                os.remove(os.path.join(current_app.static_folder, member.photo_path))
            except Exception as e:
                current_app.logger.error(f"Error deleting team member photo: {e}")
        
        db.session.delete(member)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Team member deleted successfully'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting team member: {e}")
        return jsonify({'success': False, 'message': 'An error occurred while deleting the team member'}), 500

# Company Info Routes
@bp.route('/company', methods=['GET', 'POST'])
@login_required
@admin_required
def company_info():
    company = CompanyInfo.query.first()
    if not company:
        company = CompanyInfo(
            name='KodesMind',
            tagline='Innovative Software Solutions & Digital Transformation',
            about_us='KodesMind is a leading technology company specializing in custom software development, digital transformation, and innovative solutions for modern businesses.',
            email='info@kodesmind.com',
            phone='+1 (555) KODES-01',
            address='123 Innovation Drive, Tech City, TC 12345',
            facebook_url='https://facebook.com/kodesmind',
            twitter_url='https://twitter.com/kodesmind',
            linkedin_url='https://linkedin.com/company/kodesmind',
            instagram_url='https://instagram.com/kodesmind',
            youtube_url='https://youtube.com/kodesmind',
            map_embed_code='<iframe src="https://www.google.com/maps/embed?pb=..." width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy"></iframe>',
            seo_title='KodesMind - Innovative Software Solutions & Digital Transformation',
            seo_description='Leading technology company providing custom software development, web applications, mobile apps, and digital transformation services.',
            seo_keywords='software development, web development, mobile apps, digital transformation, KodesMind, technology solutions',
            google_analytics_code='',
            facebook_pixel_code='',
            custom_css='',
            custom_js='',
            is_active=True
        )
        db.session.add(company)
        db.session.commit()
    
    form = CompanyInfoForm(obj=company)
    
    if form.validate_on_submit():
        form.populate_obj(company)
        
        # Handle logo upload
        if 'logo' in request.files:
            file = request.files['logo']
            if file.filename:
                file_path = save_file(file, 'logo')
                if file_path:
                    # Delete old logo if exists
                    if company.logo_path and os.path.exists(os.path.join(current_app.static_folder, company.logo_path)):
                        try:
                            os.remove(os.path.join(current_app.static_folder, company.logo_path))
                        except:
                            pass
                    company.logo_path = file_path
        
        # Handle favicon upload
        if 'favicon' in request.files:
            file = request.files['favicon']
            if file.filename:
                file_path = save_file(file, 'favicon')
                if file_path:
                    # Delete old favicon if exists
                    if company.favicon_path and os.path.exists(os.path.join(current_app.static_folder, company.favicon_path)):
                        try:
                            os.remove(os.path.join(current_app.static_folder, company.favicon_path))
                        except:
                            pass
                    company.favicon_path = file_path
        
        db.session.commit()
        flash('Company information updated successfully!', 'success')
        return redirect(url_for('admin.company_info'))
    
    return render_template('admin/company_info.html', form=form, company=company, title='Company Information')

# Service Management Routes
@bp.route('/services')
@login_required
@admin_required
def services():
    services = Service.query.order_by(Service.order_position.asc(), Service.title.asc()).all()
    # CSRF token is automatically available in templates via csrf_token()
    # No need to explicitly pass it
    return render_template('admin/services.html', services=services)

@bp.route('/services/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_service():
    form = ServiceForm()
    if form.validate_on_submit():
        service = Service()
        form.populate_obj(service)
        
        # Handle file upload
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                filename = secure_filename(file.filename)
                upload_folder = os.path.join(current_app.static_folder, 'uploads', 'service')
                os.makedirs(upload_folder, exist_ok=True)
                filepath = os.path.join('uploads', 'service', filename)
                file.save(os.path.join(current_app.static_folder, filepath))
                service.image_path = filepath
        
        db.session.add(service)
        db.session.commit()
        flash('Service added successfully!', 'success')
        return redirect(url_for('admin.services'))
    
    return render_template('admin/service_form.html', form=form, title='Add Service')

@bp.route('/services/<int:service_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_service(service_id):
    service = Service.query.get_or_404(service_id)
    form = ServiceForm(obj=service)
    
    if form.validate_on_submit():
        # Handle file upload
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                # Delete old image if exists
                if service.image_path and os.path.exists(os.path.join(current_app.static_folder, service.image_path)):
                    try:
                        os.remove(os.path.join(current_app.static_folder, service.image_path))
                    except Exception as e:
                        current_app.logger.error(f"Error deleting old image: {e}")
                
                # Save new image
                filename = secure_filename(file.filename)
                upload_folder = os.path.join(current_app.static_folder, 'uploads', 'service')
                os.makedirs(upload_folder, exist_ok=True)
                filepath = os.path.join('uploads', 'service', filename)
                file.save(os.path.join(current_app.static_folder, filepath))
                service.image_path = filepath
        
        form.populate_obj(service)
        service.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Service updated successfully!', 'success')
        return redirect(url_for('admin.services'))
    
    return render_template('admin/service_form.html', form=form, service=service, title='Edit Service')

@bp.route('/services/<int:service_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_service(service_id):
    # The @admin_required decorator already checks for admin status
    # This additional check is redundant but kept for extra security
    
    service = Service.query.get_or_404(service_id)
    
    # Delete associated image if exists
    if service.image_path and os.path.exists(os.path.join(current_app.static_folder, service.image_path)):
        try:
            os.remove(os.path.join(current_app.static_folder, service.image_path))
        except Exception as e:
            current_app.logger.error(f"Error deleting service image: {e}")
    
    db.session.delete(service)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Service deleted successfully'}), 200

# Portfolio Management Routes
@bp.route('/portfolio')
@login_required
def portfolio():
    projects = Portfolio.query.all()
    return render_template('admin/portfolio.html', projects=projects, title='Portfolio Management')

@bp.route('/portfolio/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_portfolio():
    form = PortfolioForm()
    
    if form.validate_on_submit():
        try:
            # Create portfolio project manually to avoid FileStorage issue
            project = Portfolio(
                project_name=form.project_name.data,
                description=form.description.data,
                client=form.client.data,
                project_date=form.project_date.data,
                project_url=form.project_url.data,
                is_featured=form.is_featured.data
            )
            
            # Handle multiple image uploads
            if 'images' in request.files:
                files = request.files.getlist('images')
                for idx, file in enumerate(files):
                    if file and file.filename:
                        file_path = save_file(file, 'portfolio')
                        if file_path:
                            is_primary = (idx == 0)  # First image is primary
                            image = PortfolioImage(
                                image_path=file_path,
                                is_primary=is_primary
                            )
                            project.images.append(image)
            
            db.session.add(project)
            db.session.commit()
            flash('Portfolio project added successfully!', 'success')
            return redirect(url_for('admin.portfolio'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error adding portfolio: {e}")
            flash('An error occurred while adding the portfolio project.', 'error')
    
    return render_template('admin/portfolio_form.html', form=form, title='Add Portfolio Project')

@bp.route('/portfolio/<int:portfolio_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_portfolio(portfolio_id):
    project = Portfolio.query.get_or_404(portfolio_id)
    form = PortfolioForm(obj=project)
    
    if form.validate_on_submit():
        try:
            # Update portfolio fields manually
            project.project_name = form.project_name.data
            project.description = form.description.data
            project.client = form.client.data
            project.project_date = form.project_date.data
            project.project_url = form.project_url.data
            project.is_featured = form.is_featured.data
            
            # Handle new image uploads
            if 'images' in request.files:
                files = request.files.getlist('images')
                for file in files:
                    if file and file.filename:
                        file_path = save_file(file, 'portfolio')
                        if file_path:
                            # Check if this is the first image
                            is_primary = len(project.images) == 0
                            image = PortfolioImage(
                                image_path=file_path,
                                is_primary=is_primary,
                                portfolio_id=project.id
                            )
                            project.images.append(image)
            
            db.session.commit()
            flash('Portfolio project updated successfully!', 'success')
            return redirect(url_for('admin.portfolio'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating portfolio: {e}")
            flash('An error occurred while updating the portfolio project.', 'error')
    
    return render_template('admin/portfolio_form.html', form=form, project=project, title='Edit Portfolio Project')

@bp.route('/portfolio/<int:portfolio_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_portfolio(portfolio_id):
    if request.method == 'POST':
        project = Portfolio.query.get_or_404(portfolio_id)
        project_name = project.project_name
        
        try:
            # Delete all associated images
            for image in project.images:
                if image.image_path and os.path.exists(os.path.join(current_app.static_folder, image.image_path)):
                    try:
                        os.remove(os.path.join(current_app.static_folder, image.image_path))
                    except Exception as e:
                        current_app.logger.error(f"Error deleting portfolio image: {e}")
            
            db.session.delete(project)
            db.session.commit()
            
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': True, 
                    'message': f'Project "{project_name}" deleted successfully',
                    'redirect': url_for('admin.portfolio')
                })
            else:
                flash(f'Project "{project_name}" has been deleted successfully!', 'success')
                return redirect(url_for('admin.portfolio'))
                
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error deleting portfolio: {e}")
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': False, 
                    'message': f'Error deleting project: {str(e)}'
                }), 500
            else:
                flash('Error deleting project. Please try again.', 'danger')
                return redirect(url_for('admin.portfolio'))
    
    # If not a POST request or any other method
    abort(405)  # Method Not Allowed

@bp.route('/portfolio/<int:portfolio_id>/image/<int:image_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_portfolio_image(portfolio_id, image_id):
    """Delete a specific portfolio image"""
    image = PortfolioImage.query.get_or_404(image_id)
    
    if image.portfolio_id != portfolio_id:
        return jsonify({'success': False, 'message': 'Invalid image'}), 400
    
    try:
        # Delete the file
        if image.image_path and os.path.exists(os.path.join(current_app.static_folder, image.image_path)):
            try:
                os.remove(os.path.join(current_app.static_folder, image.image_path))
            except Exception as e:
                current_app.logger.error(f"Error deleting image file: {e}")
        
        db.session.delete(image)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Image deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting portfolio image: {e}")
        return jsonify({'success': False, 'message': 'An error occurred while deleting the image'}), 500

# Blog Management Routes
@bp.route('/blog')
@login_required
def blog_posts():
    posts = Blog.query.order_by(Blog.created_at.desc()).all()
    return render_template('admin/blog_posts.html', posts=posts)
@bp.route('/blog/add', methods=['GET', 'POST'])
@login_required
def add_blog_post():
    form = BlogPostForm()

    if form.validate_on_submit():
        post = Blog(
            title=form.title.data,
            content=form.content.data,
            excerpt=form.excerpt.data,
            slug=form.slug.data,
            is_published=form.is_published.data,
            author_id=current_user.id
        )

        # Handle featured image upload
        if 'featured_image' in request.files:
            file = request.files['featured_image']
            if file.filename:
                file_path = save_file(file, 'blog')
                if file_path:
                    post.featured_image = file_path

        db.session.add(post)
        db.session.commit()
        flash('Blog post created successfully!', 'success')
        return redirect(url_for('admin.blog_posts'))

    return render_template('admin/blog_form.html', form=form, title='Add Blog Post')

@bp.route('/blog/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_blog_post(post_id):
    post = Blog.query.get_or_404(post_id)
    form = BlogPostForm(obj=post)
    
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.excerpt = form.excerpt.data
        post.slug = form.slug.data
        post.is_published = form.is_published.data
        post.updated_at = datetime.utcnow()
        
        # Handle featured image upload
        if 'featured_image' in request.files:
            file = request.files['featured_image']
            if file.filename:
                file_path = save_file(file, 'blog')
                if file_path:
                    # Delete old image if exists
                    if post.featured_image and os.path.exists(os.path.join(current_app.static_folder, post.featured_image)):
                        try:
                            os.remove(os.path.join(current_app.static_folder, post.featured_image))
                        except Exception as e:
                            current_app.logger.error(f"Error deleting old featured image: {e}")
                    post.featured_image = file_path
        
        db.session.commit()
        flash('Blog post updated successfully!', 'success')
        return redirect(url_for('admin.blog_posts'))
    
    return render_template('admin/blog_form.html', form=form, title='Edit Blog Post', post=post)

@bp.route('/blog/<int:post_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_blog_post(post_id):
    post = Blog.query.get_or_404(post_id)

    try:
        # Delete featured image if exists
        if post.featured_image and os.path.exists(os.path.join(current_app.static_folder, post.featured_image)):
            try:
                os.remove(os.path.join(current_app.static_folder, post.featured_image))
            except Exception as e:
                current_app.logger.error(f"Error deleting blog post image: {e}")

        db.session.delete(post)
        db.session.commit()
        flash('Blog post deleted successfully!', 'success')
        return redirect(url_for('admin.blog_posts'))

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting blog post: {e}")
        flash('Error deleting blog post. Please try again.', 'danger')
        return redirect(url_for('admin.blog_posts'))
@bp.route('/careers')
@login_required
@admin_required
def careers():
    careers = Career.query.order_by(
        Career.is_active.desc(),
        Career.created_at.desc()
    ).all()
    return render_template('admin/careers.html', careers=careers, title='Career Management')

@bp.route('/careers/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_career():
    form = CareerForm()
    
    if form.validate_on_submit():
        try:
            career = Career()
            form.populate_obj(career)
            
            # Set default values if not provided
            if not career.job_type:
                career.job_type = 'full-time'
                
            db.session.add(career)
            db.session.commit()
            
            flash('Career opportunity added successfully!', 'success')
            
            # Check if save_and_add button was clicked
            if 'save_and_add' in request.form:
                return redirect(url_for('admin.add_career'))
            else:
                return redirect(url_for('admin.careers'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error adding career: {e}")
            flash('An error occurred while adding the career opportunity.', 'error')
    
    return render_template('admin/career_form.html', form=form, title='Add Career Opportunity')

@bp.route('/careers/<int:career_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_career(career_id):
    career = Career.query.get_or_404(career_id)
    form = CareerForm(obj=career)
    
    if form.validate_on_submit():
        try:
            form.populate_obj(career)
            db.session.commit()
            flash('Career opportunity updated successfully!', 'success')
            return redirect(url_for('admin.careers'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating career {career_id}: {e}")
            flash('An error occurred while updating the career opportunity.', 'error')
    
    return render_template('admin/career_form.html', form=form, career=career, title='Edit Career Opportunity')

@bp.route('/careers/<int:career_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_career(career_id):
    career = Career.query.get_or_404(career_id)
    
    try:
        db.session.delete(career)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Career opportunity deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting career {career_id}: {e}")
        return jsonify({'success': False, 'message': 'An error occurred while deleting the career opportunity'}), 500

@bp.route('/careers/<int:career_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_career(career_id):
    """Toggle career active status."""
    career = Career.query.get_or_404(career_id)
    
    try:
        career.is_active = not career.is_active
        db.session.commit()
        
        return jsonify({
            'success': True,
            'is_active': career.is_active,
            'message': f'Career {"activated" if career.is_active else "deactivated"} successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error toggling career {career_id}: {e}")
        return jsonify({
            'success': False, 
            'message': 'An error occurred while updating the career status'
        }), 500

@bp.route('/careers/<int:career_id>/view')
@login_required
@admin_required
def view_career(career_id):
    """View career details."""
    career = Career.query.get_or_404(career_id)
    return render_template('admin/career_detail.html', career=career)

# Contact Messages (Removed duplicate - handled below with pagination)

# User Management
@bp.route('/users')
@admin_required
def manage_users():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('admin.dashboard'))
    
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@bp.route('/users/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('admin.dashboard'))
    
    form = UserForm()
    
    if form.validate_on_submit():
        try:
            # Create new user
            user = User(
                username=form.username.data,
                email=form.email.data,
                is_admin=form.is_admin.data,
                is_active=form.is_active.data
            )
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.commit()
            
            flash('User created successfully!', 'success')
            return redirect(url_for('admin.manage_users'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating user: {e}")
            flash('An error occurred while creating the user.', 'danger')
    
    return render_template('admin/user_form.html', form=form, user=None)

@bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('admin.dashboard'))
    
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)
    form.user = user  # For validation
    
    # Don't require password for existing user
    form.password.validators = [
        Optional(),
        Length(min=8, message='Password must be at least 8 characters long')
    ]
    
    if form.validate_on_submit():
        try:
            # Update user
            user.username = form.username.data
            user.email = form.email.data
            user.is_admin = form.is_admin.data
            user.is_active = form.is_active.data
            
            # Only update password if provided
            if form.password.data:
                user.set_password(form.password.data)
            
            db.session.commit()
            
            flash('User updated successfully!', 'success')
            return redirect(url_for('admin.manage_users'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating user {user_id}: {e}")
            flash('An error occurred while updating the user.', 'danger')
    
    return render_template('admin/user_form.html', form=form, user=user)

# Admin Profile
@bp.route('/profile', methods=['GET', 'POST'])
@login_required
@admin_required
def profile():
    if request.method == 'POST':
        current_user.username = request.form.get('username', current_user.username)
        current_user.email = request.form.get('email', current_user.email)
        
        # Handle password change if provided
        new_password = request.form.get('new_password')
        if new_password:
            current_user.set_password(new_password)
            
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('admin.profile'))
        
    return render_template('admin/profile.html', title='Admin Profile')

# Message Management
@bp.route('/messages')
@login_required
@admin_required
def messages():
    page = request.args.get('page', 1, type=int)
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('admin/messages.html', messages=messages)

@bp.route('/messages/<int:message_id>/view')
@login_required
@admin_required
def view_message(message_id):
    message = ContactMessage.query.get_or_404(message_id)
    # Mark as read
    if not message.is_read:
        message.is_read = True
        db.session.commit()
    return render_template('admin/message_detail.html', message=message)

@bp.route('/messages/<int:message_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_message(message_id):
    message = ContactMessage.query.get_or_404(message_id)
    try:
        db.session.delete(message)
        db.session.commit()
        flash('Message deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting message: {e}")
        flash('Error deleting message.', 'error')
    return redirect(url_for('admin.messages'))

@bp.route('/messages/<int:message_id>/toggle-read', methods=['POST'])
@login_required
@admin_required
def toggle_message_read(message_id):
    message = ContactMessage.query.get_or_404(message_id)
    message.is_read = not message.is_read
    try:
        db.session.commit()
        return jsonify({'success': True, 'is_read': message.is_read})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error toggling message read status: {e}")
        return jsonify({'success': False}), 500

# Job Application Management
@bp.route('/applications')
@login_required
@admin_required
def applications():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    
    query = JobApplication.query.order_by(JobApplication.created_at.desc())
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    applications = query.paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/applications.html', applications=applications, status_filter=status_filter)

@bp.route('/applications/<int:application_id>/view')
@login_required
@admin_required
def view_application(application_id):
    application = JobApplication.query.get_or_404(application_id)
    # Mark as reviewed
    if not application.is_reviewed:
        application.is_reviewed = True
        db.session.commit()
    return render_template('admin/application_detail.html', application=application)

@bp.route('/applications/<int:application_id>/update-status', methods=['POST'])
@login_required
@admin_required
def update_application_status(application_id):
    application = JobApplication.query.get_or_404(application_id)
    new_status = request.form.get('status')
    
    if new_status in ['pending', 'reviewed', 'shortlisted', 'rejected', 'hired']:
        application.status = new_status
        application.updated_at = datetime.utcnow()
        
        if new_status != 'pending':
            application.is_reviewed = True
            
        try:
            db.session.commit()
            flash('Application status updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating application status: {e}")
            flash('Error updating application status.', 'error')
    else:
        flash('Invalid status.', 'error')
    
    return redirect(url_for('admin.view_application', application_id=application_id))

@bp.route('/applications/<int:application_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_application(application_id):
    application = JobApplication.query.get_or_404(application_id)
    
    # Delete resume file if exists
    if application.resume_path:
        try:
            resume_file = os.path.join(current_app.static_folder, application.resume_path)
            if os.path.exists(resume_file):
                os.remove(resume_file)
        except Exception as e:
            current_app.logger.error(f"Error deleting resume file: {e}")
    
    try:
        db.session.delete(application)
        db.session.commit()
        flash('Application deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting application: {e}")
        flash('Error deleting application.', 'error')
    
    return redirect(url_for('admin.applications'))
