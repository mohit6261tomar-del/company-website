"""
Authentication decorators for CRM system
Provides role-based access control for admin and marketing staff
"""
from functools import wraps
from flask import flash, redirect, url_for, session
from flask_login import current_user


def crm_admin_required(f):
    """
    Decorator to require CRM admin login (User with is_admin=True)
    Checks Flask-Login current_user
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is authenticated via Flask-Login
        if not current_user.is_authenticated:
            flash('Please login as admin to access this page.', 'warning')
            return redirect(url_for('crm.admin_login', next=url_for('crm.' + f.__name__, **kwargs)))
        
        # Check if user has admin privileges
        if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('main.index'))
        
        return f(*args, **kwargs)
    return decorated_function


def staff_login_required(f):
    """
    Decorator to require marketing staff login
    Checks session for staff_id (separate from Flask-Login)
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if staff is logged in via session
        if 'staff_id' not in session:
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('auth.staff_login', next=url_for('crm.' + f.__name__, **kwargs)))
        
        # Verify staff is active
        from app.models import MarketingStaff
        staff = MarketingStaff.query.get(session.get('staff_id'))
        if not staff or not staff.is_active:
            session.pop('staff_id', None)
            session.pop('staff_name', None)
            flash('Your account is inactive. Please contact admin.', 'danger')
            return redirect(url_for('auth.staff_login'))
        
        return f(*args, **kwargs)
    return decorated_function


def prevent_staff_access(f):
    """
    Decorator to prevent marketing staff from accessing admin routes
    Use this on admin-only routes to double-check
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If staff is logged in, deny access
        if 'staff_id' in session:
            flash('Access denied. This area is for administrators only.', 'danger')
            return redirect(url_for('crm.staff_dashboard'))
        return f(*args, **kwargs)
    return decorated_function


def logout_other_sessions(f):
    """
    Decorator to ensure user is not logged in to both admin and staff
    Clears conflicting sessions
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If accessing admin route, clear staff session
        if 'admin' in f.__name__ and 'staff_id' in session:
            session.pop('staff_id', None)
            session.pop('staff_name', None)
        
        # If accessing staff route, ensure admin is logged out from staff perspective
        if 'staff' in f.__name__ and current_user.is_authenticated:
            # Allow admin to view staff area if needed, or block it
            pass  # Admins can access staff area for testing
        
        return f(*args, **kwargs)
    return decorated_function
