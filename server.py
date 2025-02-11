# server.py
import os
from waitress import serve
from app import app  # Import your Flask app

if __name__ == '__main__':
    # Configure host and port
    host = os.getenv("SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("SERVER_PORT", 8080))

    print(f"Starting Waitress server on {host}:{port}...")
    print(f"http://{host}:{port}")
    
    serve(app, host=host, port=port, threads=4)  # Adjust threads based on needs

# Optional production config
from app import app
import logging

# Configure logging
logging.basicConfig(
    filename='production.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Set Flask configs for production
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=1800  # 30 minutes
)