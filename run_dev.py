"""
Development server startup script.

This script provides:
- Environment validation
- Database connection check
- Development server startup
- Error handling
"""

import os
import sys
import uvicorn
from pathlib import Path
from dotenv import load_dotenv
import traceback

# Load environment variables from .env file
load_dotenv()

# Add app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def validate_environment():
    """Validate required environment variables."""
    required_vars = ["DATABASE_URL"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"Missing environment variables: {', '.join(missing_vars)}")
        print("Please set up your .env file with the required variables.")
        return False
    
    return True

def check_database_connection():
    """Check database connectivity."""
    try:
        # Import here to avoid circular imports
        from sqlalchemy import text
        from app.database import SessionLocal
        
        db = SessionLocal()
        # Try to create a session to check the connection
        db.execute(text("SELECT 1"))
        db.close()
        print("✓ Database connection successful")
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Main startup function."""
    print("Starting Issue Tracker API Development Server...")
    print("=" * 50)
    
    # Validate environment
    if not validate_environment():
        sys.exit(1)
    
    # Check database connection
    if not check_database_connection():
        print("Please ensure your PostgreSQL server is running and accessible.")
        sys.exit(1)
    
    print("✓ Environment validation passed")
    print("✓ Starting development server...")
    print("API Documentation: http://localhost:8000/api/docs")
    print("ReDoc Documentation: http://localhost:8000/api/redoc")
    print("Health Check: http://localhost:8000/health")
    print("=" * 50)
    
    # Start the server
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",  # Changed from 0.0.0.0 to 127.0.0.1
        port=8000,
        reload=True,
        log_level="debug"  # Added for more detailed logging
    )

if __name__ == "__main__":
    main()
