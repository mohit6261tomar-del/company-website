#!/usr/bin/env python
"""
Development server startup script
"""
import os
from application import app

if __name__ == '__main__':
    # Set environment to development
    os.environ.setdefault('FLASK_ENV', 'development')
    
    # Run development server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
