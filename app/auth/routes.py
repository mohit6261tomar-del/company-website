from flask import render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse as url_parse
from datetime import datetime
from app import db
from app.auth import bp
from app.models import User, MarketingStaff
from app.auth.forms import LoginForm, RegistrationForm, StaffLoginForm


def log_audit(user_type, user_id, action, entity_type, entity_id=None, description=None):
    """Helper function to log audit trail"""
    try:
        from app.models import AuditLog
        audit = AuditLog(
            user_type=user_type,
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            ip_address=request.remote_addr
        )
        db.session.add(audit)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(f"Error logging audit: {e}")


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('crm.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password. Please check your credentials and try again.', 'danger')
            return redirect(url_for('auth.login'))
            
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('crm.index')
            
        flash(f'Welcome back, {user.username}!', 'success')
        return redirect(next_page)
    
    return render_template('auth/login.html', title='Admin Login', form=form)


@bp.route('/staff/login', methods=['GET', 'POST'])
def staff_login():
    """Marketing staff login - accessible from /auth/staff/login"""
    # Logout admin if logged in (staff and admin are separate)
    if current_user.is_authenticated:
        logout_user()
    
    # Check if staff is already logged in
    if 'staff_id' in session:
        return redirect(url_for('crm.staff_dashboard'))
    
    form = StaffLoginForm()
    if form.validate_on_submit():
        staff = MarketingStaff.query.filter_by(phone_number=form.phone_number.data).first()
        
        if staff and staff.check_password(form.password.data):
            if not staff.is_active:
                flash('Your account is inactive. Please contact administrator.', 'danger')
                log_audit('staff', staff.id, 'failed_login', 'session', description='Inactive account login attempt')
                return render_template('auth/staff_login.html', form=form, title='Staff Login')
            
            # Create staff session using Flask session
            session['staff_id'] = staff.id
            session['staff_name'] = staff.name
            session.permanent = form.remember_me.data
            staff.ping()
            
            log_audit('staff', staff.id, 'login', 'session', description='Staff logged in via auth')
            flash(f'Welcome back, {staff.name}!', 'success')
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('crm.staff_dashboard'))
        else:
            flash('Invalid phone number or password. Please check your credentials.', 'danger')
            log_audit('staff', 0, 'failed_login', 'session', description=f'Failed login attempt for {form.phone_number.data}')
    
    return render_template('auth/staff_login.html', form=form, title='Staff Login')

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            is_admin=form.is_admin.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('User registered successfully!', 'success')
        return redirect(url_for('admin.manage_users'))
    
    return render_template('auth/register.html', title='Register New User', form=form)
