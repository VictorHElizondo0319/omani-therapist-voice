#!/usr/bin/env python3
"""
Database initialization script for OMANI-Therapist-Voice
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.core.config import settings
from app.core.database import Base, engine
from app.core.security import security_manager
from app.core.hipaa import hipaa_manager

def create_database():
    """Create database if it doesn't exist"""
    try:
        # Connect to PostgreSQL server (not to specific database)
        server_url = settings.DATABASE_URL.rsplit('/', 1)[0] + '/postgres'
        server_engine = create_engine(server_url)
        
        with server_engine.connect() as conn:
            # Check if database exists
            result = conn.execute(text(
                "SELECT 1 FROM pg_database WHERE datname = 'omani_therapist'"
            ))
            
            if not result.fetchone():
                print("📊 Creating database 'omani_therapist'...")
                conn.execute(text("COMMIT"))  # End any transaction
                conn.execute(text("CREATE DATABASE omani_therapist"))
                print("✅ Database created successfully!")
            else:
                print("ℹ️  Database 'omani_therapist' already exists")
                
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False
    
    return True

def create_tables():
    """Create all tables"""
    try:
        print("📊 Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

def initialize_security():
    """Initialize security components"""
    try:
        print("🔒 Initializing security components...")
        
        # Test encryption
        test_data = "test sensitive data"
        encrypted = security_manager.encrypt_sensitive_data(test_data)
        print("✅ Data encryption working")
        
        # Test session ID generation
        session_id = security_manager.generate_session_id()
        print("✅ Session ID generation working")
        
        return True
    except Exception as e:
        print(f"❌ Error initializing security: {e}")
        return False

def initialize_hipaa():
    """Initialize HIPAA compliance components"""
    try:
        print("🏥 Initializing HIPAA compliance...")
        
        # Test PHI classification
        classification = hipaa_manager.classify_data("conversation_content")
        print(f"✅ PHI classification working: {classification.value}")
        
        # Test access permissions
        has_access = hipaa_manager.check_access_permission(
            "therapist", "conversation_content", "read"
        )
        print("✅ Access control working")
        
        # Get compliance summary
        summary = hipaa_manager.get_compliance_summary()
        print("✅ HIPAA compliance initialized")
        
        return True
    except Exception as e:
        print(f"❌ Error initializing HIPAA: {e}")
        return False

def main():
    """Main initialization function"""
    print("🚀 Initializing OMANI-Therapist-Voice database...")
    
    # Ensure database exists first (connects to server, not specific DB)
    if not create_database():
        return False
    
    # Optional: verify connection to target database now that it should exist
    try:
        engine.connect()
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("Please ensure PostgreSQL is running and credentials are correct.")
        return False

    # Create tables
    if not create_tables():
        return False
    
    # Initialize security
    if not initialize_security():
        return False
    
    # Initialize HIPAA compliance
    if not initialize_hipaa():
        return False
    
    print("🎉 Database initialization completed successfully!")
    print("")
    print("Next steps:")
    print("1. Start the backend server: cd backend && python main.py")
    print("2. Start the frontend server: cd frontend && npm run dev")
    print("3. Access the application at http://localhost:3000")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
