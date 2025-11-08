from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse as url_parse
from app import db
from app.auth import bp
from app.models import User
from app.auth.forms import LoginForm, RegistrationForm

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))
            
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('admin.dashboard')
            
        return redirect(next_page)
    
    return render_template('auth/login.html', title='Sign In', form=form)

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
