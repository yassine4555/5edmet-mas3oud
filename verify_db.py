import os
import sys
from datetime import datetime

# Add current directory to path
sys.path.append(os.getcwd())

from app import app
from models import db, User, Meeting, Activity

def verify_database():
    print("🚀 Starting Database Verification...")
    
    with app.app_context():
        try:
            # 1. Test Connection
            print("1️⃣  Testing Database Connection...")
            db.session.execute(db.text('SELECT 1'))
            print("✅ Database Connection Successful!")
            
            # 2. Check Tables
            print("\n2️⃣  Checking Models...")
            
            # Check User model
            user_count = User.query.count()
            print(f"   - Users found: {user_count}")
            
            # Check Meeting model
            meeting_count = Meeting.query.count()
            print(f"   - Meetings found: {meeting_count}")
            
            # Check Activity model (Newly added)
            activity_count = Activity.query.count()
            print(f"   - Activities found: {activity_count}")
            print("✅ Models accessed successfully!")

            # 3. Test Activity Creation (Rollback after)
            print("\n3️⃣  Testing Activity Creation...")
            try:
                # Create a test user if none exists (just for foreign key)
                test_user = User.query.first()
                if not test_user:
                    print("   ⚠️  No users found. Skipping activity creation test (requires user).")
                else:
                    new_activity = Activity(
                        type='test',
                        title='Test Activity',
                        description='Verifying database write',
                        creator=test_user.email,
                        date=datetime.now()
                    )
                    db.session.add(new_activity)
                    db.session.flush() # Check for errors without committing
                    print(f"   - Created activity ID: {new_activity.activity_id}")
                    db.session.rollback() # Clean up
                    print("✅ Activity creation verified (rolled back)!")
            except Exception as e:
                print(f"❌ Failed to create activity: {e}")
                raise e

        except Exception as e:
            print(f"\n❌ Verification FAILED: {e}")
            sys.exit(1)
            
    print("\n✨ Database Verification Completed Successfully!")

if __name__ == "__main__":
    verify_database()
