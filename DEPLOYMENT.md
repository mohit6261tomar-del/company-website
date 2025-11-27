# Deployment Guide

## Project Structure
- **Cleaned up**: Removed unnecessary test files, duplicate models, and migration scripts
- **Database**: Set up with proper migrations and initial data
- **Production ready**: Added configuration files for deployment

## Database Setup
Run the database setup script to create tables and initial data:
```bash
python setup_database.py
```

This creates:
- All database tables
- Default admin user (username: `admin`, password: `admin123`)
- Sample company information

## Development Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your settings

# Run development server
python run.py
```

## Production Deployment

### Option 1: Traditional Server
```bash
# Install production dependencies
pip install -r requirements.txt

# Set production environment
export FLASK_ENV=production
export DATABASE_URL=mysql+pymysql://user:password@localhost/company_db
export SECRET_KEY=your-secret-key

# Run with Gunicorn
gunicorn --config gunicorn_config.py wsgi:app
```

### Option 2: Docker
```bash
# Build and run with Docker Compose (MySQL)
docker-compose up --build
```

### Option 3: Heroku
```bash
# Deploy to Heroku
heroku create your-app-name
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DATABASE_URL=mysql+pymysql://user:password@host/dbname
git push heroku main
```

## Environment Variables
- `SECRET_KEY`: Flask secret key (required for production)
- `DATABASE_URL`: Database connection string
- `FLASK_ENV`: Environment (development/production)

## File Uploads
- Upload directory: `app/static/uploads/`
- Max file size: 16MB
- Allowed formats: PNG, JPG, JPEG, GIF, PDF, DOC, DOCX

## Security Features
- CSRF protection enabled
- Secure session cookies in production
- Password hashing with bcrypt
- SQL injection protection via SQLAlchemy

## Admin Access
- URL: `/admin`
- Default credentials: `admin` / `admin123`
- **Important**: Change default password in production

## Database Migrations
```bash
# Create new migration
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade
```

## Monitoring
- Application logs available via Gunicorn
- Database connection monitoring
- Error tracking recommended (Sentry, etc.)
