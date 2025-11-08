from app import create_app, db
from app.models import User, CompanyInfo, Team, Service, Portfolio, Blog, Career, ContactMessage, JobApplication

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'CompanyInfo': CompanyInfo,
        'Team': Team,
        'Service': Service,
        'Portfolio': Portfolio,
        'Blog': Blog,
        'Career': Career,
        'ContactMessage': ContactMessage,
        'JobApplication': JobApplication
    }

if __name__ == '__main__':
    app.run(debug=True)
