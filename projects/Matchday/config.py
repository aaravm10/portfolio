import os
from datetime import date


_TRUTHY_DEBUG_VALUES = {'true', '1', 't'}


class Config:
    """Application configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'matchday-secret-key-change-in-production'
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    
    # Database configuration
    DATABASE_URI = os.environ.get('DATABASE_URI') or 'sqlite:///usersdb.db'

    # Application settings
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() in _TRUTHY_DEBUG_VALUES

    # Chart settings
    AX_BG = "#071421"
    SEPARATOR_COLOR = "#ffffff"

    # Season calculation
    today = date.today()
    SEASON = str(today.year if today.month >= 7 else today.year - 1)

    # File paths
    DATA_DIR = "data"
    IMAGES_DIR = "static/images"
