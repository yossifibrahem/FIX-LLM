# server.py
from waitress import serve
from app import app  # Import your Flask app

if __name__ == '__main__':
    # Configure host and port
    host = '127.0.0.1'  # localhost
    port = 8080        # Choose your preferred port
    
    print(f"Starting Waitress server on {host}:{port}...")
    print(f"http://{host}:{port}")
    serve(app, host=host, port=port, threads=4)  # Adjust number of threads based on your needs

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