# Company Website

A full-featured company website built with Flask, providing both a public-facing marketing site and an admin dashboard for managing content, team members, careers, and incoming leads.

## Features

- **Marketing site**: Home, About, Services, Portfolio, Blog, Careers, and Contact pages backed by a relational database.
- **Contact & careers workflows**: Collect enquiries and job applications with form validation, file uploads, and CSRF protection.
- **Dynamic blog**: Publish posts with slugs, excerpts, featured images, tags, and categories.
- **Portfolio management**: Showcase projects with image galleries, featured projects, and completion timelines.
- **Admin dashboard**: Manage company info, services, team, blog posts, portfolio items, career listings, and messages with role-based access control.
- **Analytics & utilities**: Track page views, unread messages, and recent activity from the dashboard.

## Technology Stack

- Python 3.10+
- Flask 2.3
- SQLAlchemy & Flask-Migrate
- Flask-WTF & WTForms
- Flask-Login & Flask-Bcrypt
- SQLite (development default) or any SQLAlchemy-compatible database
- Jinja2 templates with Bootstrap-based styling (customizable in `app/static/`)

## Getting Started

### 1. Clone and set up a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate           # macOS/Linux
.venv\Scripts\activate             # Windows
pip install -r requirements.txt
```

### 2. Configure environment variables

Create a `.env` file in the project root (or set system environment variables) with at least:

```dotenv
FLASK_ENV=development
SECRET_KEY=change-me
DATABASE_URL=sqlite:///site.db  # Optional; defaults to SQLite in instance/site.db
```

### 3. Initialize the database

```bash
# macOS/Linux
export FLASK_APP=run.py
flask db upgrade

# Windows (PowerShell)
$env:FLASK_APP = "run.py"
flask db upgrade
```

The default configuration points to an SQLite database stored in `instance/site.db`. Adjust `DATABASE_URL` for other databases.

### 4. Create an admin user

Run the helper script to create or update an admin account (default credentials: `admin` / `admin123`). Change the password after the first login.

```bash
python create_admin.py
```

### 5. Launch the development server

```bash
flask run
```

Visit `http://127.0.0.1:5000/` for the public site and `http://127.0.0.1:5000/admin/` for the dashboard (requires admin login).

## Project Structure

```
COMPANY WEBSITE/
├── app/
│   ├── __init__.py          # Application factory & extension setup
│   ├── admin/               # Admin blueprint, forms, and routes
│   ├── auth/                # Authentication blueprint (login, registration)
│   ├── main/                # Public-facing routes and views
│   ├── models.py            # Database models
│   ├── forms.py             # Reusable WTForms definitions
│   ├── static/              # CSS, JS, images, uploads
│   └── templates/           # Jinja2 templates for all blueprints
├── instance/
│   └── site.db              # SQLite database (generated at runtime)
├── migrations/              # Alembic migration history
├── requirements.txt         # Python dependencies
├── run.py                   # WSGI entrypoint & shell context
├── create_admin.py          # Utility script for admin account
└── README.md
```

Additional helper scripts (e.g., `populate_services.py`, `add_blog_data.py`) can seed demo content.

## Useful Commands

- `flask shell` — loads an interactive shell with `db`, `User`, `CompanyInfo`, and other models pre-imported (see `run.py`).
- `flask db migrate -m "message"` followed by `flask db upgrade` — manage database migrations.
- `python test_admin_panel.py` — run available test scripts (if any) and extend as needed.

## Deployment Notes

- Replace the development `SECRET_KEY` and `DATABASE_URL` with production values.
- Serve the app through a WSGI server (e.g., Gunicorn, uWSGI) behind a reverse proxy.
- Configure static file hosting (built assets live in `app/static/`).
- Update `.env` or system variables to include analytics IDs, SMTP settings, and any third-party integrations.

## License

This project does not currently specify a license. Add one (`LICENSE` file) before distributing or deploying publicly.
