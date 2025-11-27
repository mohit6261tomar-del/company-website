"""
WSGI entry point for production deployment
"""
import os
from application import app

# Set environment variables
os.environ.setdefault('FLASK_ENV', 'production')

if __name__ == "__main__":
    app.run()
