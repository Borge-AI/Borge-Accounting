#!/usr/bin/env python3
"""
Script to create an admin user.
Usage: python scripts/create_admin.py <email> <password> <full_name>
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db import models
from app.core.security import get_password_hash


def create_admin(email: str, password: str, full_name: str):
    """Create an admin user."""
    db: Session = SessionLocal()
    
    try:
        # Check if user exists
        existing_user = db.query(models.User).filter(models.User.email == email).first()
        if existing_user:
            print(f"User with email {email} already exists!")
            return False
        
        # Create admin user
        admin = models.User(
            email=email,
            hashed_password=get_password_hash(password),
            full_name=full_name,
            role=models.UserRole.ADMIN,
            is_active=True
        )
        
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        print(f"Admin user created successfully!")
        print(f"Email: {admin.email}")
        print(f"Name: {admin.full_name}")
        print(f"Role: {admin.role}")
        
        return True
    except Exception as e:
        db.rollback()
        print(f"Error creating admin user: {str(e)}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python scripts/create_admin.py <email> <password> <full_name>")
        sys.exit(1)
    
    email = sys.argv[1]
    password = sys.argv[2]
    full_name = sys.argv[3]
    
    success = create_admin(email, password, full_name)
    sys.exit(0 if success else 1)
