import os

# Flask configuration
SECRET_KEY = os.urandom(24)
DEBUG = True

# Database configuration
DATABASE_URI = 'sqlite:///database.db'

# OTP configuration
OTP_EXPIRY_MINUTES = 5
OTP_LENGTH = 6

# Admin credentials
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'  # In production, use hashed password

# Voting configuration
VOTING_TIME_SECONDS = 20