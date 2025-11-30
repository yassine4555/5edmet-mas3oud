"""Check existing users in the database."""
from app import app, db
from models import User

def check_users():
    with app.app_context():
        users = User.query.all()
        
        if not users:
            print("No users in database.")
            return
        
        print(f"\n=== Found {len(users)} users ===\n")
        for user in users:
            print(f"ID: {user.id}")
            print(f"Email: {user.email}")
            print(f"UserID: {user.user_id}")
            print(f"Name: {user.first_name} {user.last_name}")
            print(f"Role: {user.role}")
            print("-" * 50)

if __name__ == '__main__':
    check_users()
