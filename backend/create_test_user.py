"""
Create a test user for development
"""
from app.database import SessionLocal
from app.models.database import User
from app.utils.auth import get_password_hash

def create_test_user():
    db = SessionLocal()
    try:
        # Check if test user already exists
        existing_user = db.query(User).filter(User.email == "test@example.com").first()
        if existing_user:
            print("✓ Test user already exists!")
            print(f"  Email: {existing_user.email}")
            print(f"  Username: {existing_user.username}")
            print("  Password: test123")
            return
        
        # Create test user
        test_user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=get_password_hash("test123"),
            full_name="Test User"
        )
        
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        print("✓ Test user created successfully!")
        print(f"  Email: {test_user.email}")
        print(f"  Username: {test_user.username}")
        print("  Password: test123")
        
    except Exception as e:
        print(f"Error creating test user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()
