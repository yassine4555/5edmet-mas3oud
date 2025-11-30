"""Configuration settings for the application."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class."""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Database settings
    # Default to localhost for running outside docker, or use service name 'db' inside docker
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://admin:password@localhost:5432/savingdb'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File Upload
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', './storage/files')
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB max file size
    
    # Internal Security
    INTERNAL_API_KEY = os.getenv('INTERNAL_API_KEY', 'nexus-internal-secret-key-123')
