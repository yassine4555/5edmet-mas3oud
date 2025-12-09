"""
Integration Tests for DAO/Repository Layer
Tests database operations with actual SQLite database
"""
import unittest
import os
from datetime import datetime, timedelta
from flask import Flask
from models.database import db
from models import User, Invite, File, Meeting, Activity

class TestDAOIntegration(unittest.TestCase):
    """Integration tests for Data Access Objects"""
    
    def setUp(self):
        """Set up test database"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        db.init_app(self.app)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        """Clean up test database"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # ========== User Repository Tests ==========
    
    def test_user_crud_operations(self):
        """Test Create, Read, Update, Delete operations for User"""
        print("\n=== Testing User CRUD ===")
        
        # CREATE
        user = User(
            email='test@example.com',
            user_id='auth0_123',
            first_name='Test',
            last_name='User',
            role='employee',
            department='IT',
            address='123 Test St',
            date_of_birth=datetime(1990, 1, 1)
        )
        db.session.add(user)
        db.session.commit()
        
        # READ
        retrieved = User.query.filter_by(email='test@example.com').first()
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.first_name, 'Test')
        
        # UPDATE
        retrieved.department = 'Engineering'
        db.session.commit()
        updated = User.query.filter_by(email='test@example.com').first()
        self.assertEqual(updated.department, 'Engineering')
        
        # DELETE
        db.session.delete(updated)
        db.session.commit()
        deleted = User.query.filter_by(email='test@example.com').first()
        self.assertIsNone(deleted)
        
        print("✅ User CRUD operations passed")

    def test_user_relationships(self):
        """Test User relationships with other entities"""
        print("\n=== Testing User Relationships ===")
        
        # Create manager
        manager = User(
            email='manager@example.com',
            user_id='auth0_mgr',
            first_name='Manager',
            last_name='One',
            role='manager'
        )
        db.session.add(manager)
        db.session.commit()
        
        # Create employee
        employee = User(
            email='employee@example.com',
            user_id='auth0_emp',
            first_name='Employee',
            last_name='One',
            role='employee'
        )
        db.session.add(employee)
        db.session.commit()
        
        # Test manager-employee relationship via employees_list
        manager.employees_list = ['employee@example.com']
        db.session.commit()
        
        retrieved_manager = User.query.filter_by(email='manager@example.com').first()
        self.assertIn('employee@example.com', retrieved_manager.employees_list)
        
        print("✅ User relationships passed")

    # ========== Activity Repository Tests ==========
    
    def test_activity_crud_operations(self):
        """Test CRUD operations for Activity"""
        print("\n=== Testing Activity CRUD ===")
        
        # Create user first (foreign key requirement)
        user = User(
            email='creator@example.com',
            user_id='auth0_creator',
            first_name='Creator',
            last_name='User',
            role='manager'
        )
        db.session.add(user)
        db.session.commit()
        
        # CREATE Activity
        activity = Activity(
            type='meeting',
            title='Team Sync',
            description='Weekly sync',
            creator='creator@example.com',
            date=datetime.now() + timedelta(days=1),
            status='scheduled'
        )
        db.session.add(activity)
        db.session.commit()
        
        # READ
        retrieved = Activity.query.filter_by(title='Team Sync').first()
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.creator, 'creator@example.com')
        
        # UPDATE
        retrieved.status = 'completed'
        db.session.commit()
        updated = Activity.query.filter_by(title='Team Sync').first()
        self.assertEqual(updated.status, 'completed')
        
        # DELETE
        db.session.delete(updated)
        db.session.commit()
        deleted = Activity.query.filter_by(title='Team Sync').first()
        self.assertIsNone(deleted)
        
        print("✅ Activity CRUD operations passed")

    def test_activity_participants(self):
        """Test Activity participant management"""
        print("\n=== Testing Activity Participants ===")
        
        # Create users
        creator = User(email='creator@example.com', user_id='auth0_c', first_name='C', last_name='U', role='manager')
        participant1 = User(email='p1@example.com', user_id='auth0_p1', first_name='P1', last_name='U', role='employee')
        participant2 = User(email='p2@example.com', user_id='auth0_p2', first_name='P2', last_name='U', role='employee')
        
        db.session.add_all([creator, participant1, participant2])
        db.session.commit()
        
        # Create activity
        activity = Activity(
            type='workshop',
            title='Training',
            creator='creator@example.com',
            date=datetime.now()
        )
        db.session.add(activity)
        db.session.commit()
        
        # Add participants
        activity.add_employee('p1@example.com')
        activity.add_employee('p2@example.com')
        db.session.commit()
        
        # Verify
        retrieved = Activity.query.filter_by(title='Training').first()
        self.assertIn('p1@example.com', retrieved.employees_joined)
        self.assertIn('p2@example.com', retrieved.employees_joined)
        
        # Remove participant
        retrieved.remove_employee('p1@example.com')
        db.session.commit()
        
        updated = Activity.query.filter_by(title='Training').first()
        self.assertNotIn('p1@example.com', updated.employees_joined)
        self.assertIn('p2@example.com', updated.employees_joined)
        
        print("✅ Activity participants management passed")

    # ========== Meeting Repository Tests ==========
    
    def test_meeting_crud_operations(self):
        """Test CRUD operations for Meeting"""
        print("\n=== Testing Meeting CRUD ===")
        
        # Create creator
        creator = User(email='host@example.com', user_id='auth0_host', first_name='Host', last_name='User', role='manager')
        db.session.add(creator)
        db.session.commit()
        
        # CREATE - Use created_by (the actual FK field name)
        meeting = Meeting(
            meeting_id='meeting_123',
            title='Sprint Planning',
            description='Plan next sprint',
            created_by='host@example.com',  # Correct FK field
            is_active=True
        )
        db.session.add(meeting)
        db.session.commit()
        
        # READ
        retrieved = Meeting.query.filter_by(title='Sprint Planning').first()
        self.assertIsNotNone(retrieved)
        self.assertTrue(retrieved.is_active)
        self.assertEqual(retrieved.created_by, 'host@example.com')
        
        # UPDATE
        retrieved.description = 'Updated description'
        db.session.commit()
        updated = Meeting.query.filter_by(title='Sprint Planning').first()
        self.assertEqual(updated.description, 'Updated description')
        
        # SOFT DELETE
        retrieved.is_active = False
        db.session.commit()
        soft_deleted = Meeting.query.filter_by(title='Sprint Planning').first()
        self.assertFalse(soft_deleted.is_active)
        
        print("✅ Meeting CRUD operations passed")

    # ========== File Repository Tests ==========
    
    def test_file_crud_operations(self):
        """Test CRUD operations for File"""
        print("\n=== Testing File CRUD ===")
        
        # Create uploader
        uploader = User(email='uploader@example.com', user_id='auth0_up', first_name='Up', last_name='Loader', role='employee')
        db.session.add(uploader)
        db.session.commit()
        
        # CREATE
        file = File(
            file_id='file_123',
            filename='document.pdf',
            original_filename='My Document.pdf',
            size=1024,
            content_type='application/pdf',
            uploaded_by='uploader@example.com',
            file_path='/storage/document.pdf'
        )
        db.session.add(file)
        db.session.commit()
        
        # READ
        retrieved = File.query.filter_by(file_id='file_123').first()
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.filename, 'document.pdf')
        
        # UPDATE
        retrieved.size = 2048
        db.session.commit()
        updated = File.query.filter_by(file_id='file_123').first()
        self.assertEqual(updated.size, 2048)
        
        # DELETE
        db.session.delete(updated)
        db.session.commit()
        deleted = File.query.filter_by(file_id='file_123').first()
        self.assertIsNone(deleted)
        
        print("✅ File CRUD operations passed")

    # ========== Complex Query Tests ==========
    
    def test_complex_queries(self):
        """Test complex database queries"""
        print("\n=== Testing Complex Queries ===")
        
        # Create test data
        users = [
            User(email=f'user{i}@example.com', user_id=f'auth0_{i}', first_name=f'User{i}', last_name='Test', role='employee')
            for i in range(5)
        ]
        db.session.add_all(users)
        db.session.commit()
        
        # Query by role
        employees = User.query.filter_by(role='employee').all()
        self.assertEqual(len(employees), 5)
        
        # Query with LIKE
        users_with_1 = User.query.filter(User.email.like('%user1%')).all()
        self.assertEqual(len(users_with_1), 1)
        
        # Count query
        total_users = User.query.count()
        self.assertEqual(total_users, 5)
        
        print("✅ Complex queries passed")

    def test_transaction_rollback(self):
        """Test transaction rollback on error"""
        print("\n=== Testing Transaction Rollback ===")
        
        try:
            # Start transaction
            user = User(
                email='rollback@example.com',
                user_id='auth0_rollback',
                first_name='Rollback',
                last_name='Test',
                role='employee'
            )
            db.session.add(user)
            
            # Force an error (duplicate email)
            duplicate = User(
                email='rollback@example.com',  # Same email
                user_id='auth0_duplicate',
                first_name='Duplicate',
                last_name='Test',
                role='employee'
            )
            db.session.add(duplicate)
            db.session.commit()
            
            self.fail("Should have raised an exception")
        except Exception:
            db.session.rollback()
            
        # Verify rollback
        user_count = User.query.filter_by(email='rollback@example.com').count()
        self.assertEqual(user_count, 0)
        
        print("✅ Transaction rollback passed")

if __name__ == '__main__':
    print("Starting DAO/Repository Integration Tests...")
    print("=" * 60)
    unittest.main(verbosity=2)
