from flask import Blueprint, render_template, redirect, url_for, flash

bp = Blueprint('crm', __name__)

from app.crm import routes

# Error handlers for CRM blueprint
@bp.app_errorhandler(403)
def forbidden(error):
    """Handle 403 Forbidden errors"""
    flash('Access denied. You do not have permission to access this resource.', 'danger')
    return redirect(url_for('crm.index')), 403

@bp.app_errorhandler(401)
def unauthorized(error):
    """Handle 401 Unauthorized errors"""
    flash('Please login to access this page.', 'warning')
    return redirect(url_for('crm.index')), 401
