from setuptools import setup, find_packages

setup(
    name="your_application",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'flask',
        'flask-sqlalchemy',
        'flask-login',
        'flask-wtf',
        'flask-migrate',
        'python-dotenv',
        'email-validator',
        'pillow',
        'flask-bcrypt',
        'pymysql'
    ],
)
