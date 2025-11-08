import os
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
from markupsafe import Markup

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()

def timesince(dt, default="just now"):
    """
    Returns string representing "time since" e.g.
    3 days ago, 5 hours ago etc.
    """
    if dt is None:
        return default
        
    now = datetime.utcnow()
    diff = now - dt
    
    periods = [
        (diff.days // 365, 'year', 'years'),
        (diff.days % 365 // 30, 'month', 'months'),
        (diff.days % 30 // 7, 'week', 'weeks'),
        (diff.days % 7, 'day', 'days'),
        (diff.seconds // 3600, 'hour', 'hours'),
        (diff.seconds % 3600 // 60, 'minute', 'minutes'),
        (diff.seconds % 60, 'second', 'seconds'),
    ]
    
    for period, singular, plural in periods:
        if period >= 1:
            return f"{period} {singular if period == 1 else plural} ago"
    
    return default

def create_app():
    # Create and configure the app
    app = Flask(__name__)
    
    # Add custom Jinja2 filters
    app.jinja_env.filters['timesince'] = timesince
    app.jinja_env.filters['nl2br'] = lambda value: Markup(value.replace('\n', '<br>')) if value else ''
    
    # Load environment variables
    load_dotenv()
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-123')
    # Use SQLite for development
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///site.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions with app
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    migrate.init_app(app, db)
    csrf.init_app(app)
    
    # Register blueprints
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Create database tables
    with app.app_context():
        from app import models
    
    @app.context_processor
    def inject_globals():
        from datetime import datetime
        from app.models import ContactMessage, CompanyInfo
        from flask_login import current_user
        
        def get_unread_messages_count():
            if current_user.is_authenticated and current_user.is_admin:
                try:
                    return ContactMessage.query.filter_by(is_read=False).count()
                except:
                    return 0
            return 0
        
        # Get company info for all templates
        company = None
        try:
            company = CompanyInfo.query.first()
        except:
            pass
            
        return {
            'now': datetime.utcnow(),
            'get_unread_messages_count': get_unread_messages_count,
            'company': company
        }
    
    return app

from app import models
