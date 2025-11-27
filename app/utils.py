from functools import wraps
from flask import flash, redirect, url_for, abort
from flask_login import current_user

def admin_required(f):
    """Decorator to ensure the user has admin privileges."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Access denied. Admin login required.', 'danger')
            return redirect(url_for('crm.index'))
        return f(*args, **kwargs)
    return decorated_function

def save_file(file, folder='static/uploads'):
    """Save uploaded file to the specified folder."""
    import os
    from werkzeug.utils import secure_filename
    
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(folder, filename)
        file.save(filepath)
        return filepath
    return None
