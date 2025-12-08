import unittest
import os
from flask import Flask
from models.database import db
from models import User, Invite, File, Activity
from datetime import datetime

class TestDatabaseModels(unittest.TestCase):
    def setUp(self):
        # Create a fresh app for testing
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Initialize db with this app
        db.init_app(self.app)
        
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Drop all first to be sure
        db.drop_all()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        # Clean up file
        if os.path.exists('test.db'):
            try:
                os.remove('test.db')
            except:
                pass

    def test_user_creation(self):
        print("Testing user creation...")
        user = User(
            email='test@example.com',
            user_id='auth0_test_123',
            first_name='Test',
            last_name='User',
            role='employee',
            department='QA',
            address='123 Test St',
            date_of_birth=datetime(1990, 1, 1)
        )
        db.session.add(user)
        db.session.commit()
        
        retrieved = User.query.filter_by(email='test@example.com').first()
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.first_name, 'Test')
        self.assertEqual(retrieved.role, 'employee')

    def test_invite_creation(self):
        print("Testing invite creation...")
        manager = User(
            email='manager@example.com',
            user_id='auth0_manager_456',
            first_name='Manager',
            last_name='User',
            role='manager'
        )
        db.session.add(manager)
        db.session.commit()
        
        invite = Invite(
            manager_id='auth0_manager_456',
            code='TESTCODE',
            max_uses=5
        )
        db.session.add(invite)
        db.session.commit()
        
        retrieved = Invite.query.filter_by(code='TESTCODE').first()
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.max_uses, 5)

    def test_file_creation(self):
        print("Testing file creation...")
        user = User(
            email='uploader@example.com',
            user_id='auth0_uploader_789',
            first_name='Uploader',
            last_name='User',
            role='employee'
        )
        db.session.add(user)
        db.session.commit()
        
        file = File(
            file_id='file_123',
            filename='test.pdf',
            original_filename='test.pdf',
            size=1024,
            content_type='application/pdf',
            uploaded_by='uploader@example.com',
            file_path='/tmp/test.pdf'
        )
        db.session.add(file)
        db.session.commit()
        
        retrieved = File.query.filter_by(file_id='file_123').first()
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.filename, 'test.pdf')

    def test_activity_creation(self):
        print("Testing activity creation...")
        user = User(
            email='creator@example.com',
            user_id='auth0_creator_999',
            first_name='Creator',
            last_name='User',
            role='manager'
        )
        db.session.add(user)
        db.session.commit()
        
        activity = Activity(
            type='meeting',
            title='Team Sync',
            description='Weekly sync',
            creator='creator@example.com',
            date=datetime(2025, 1, 1, 10, 0),
            status='scheduled'
        )
        db.session.add(activity)
        db.session.commit()
        
        retrieved = Activity.query.filter_by(title='Team Sync').first()
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.creator, 'creator@example.com')
        self.assertEqual(retrieved.status, 'scheduled')

if __name__ == '__main__':
    unittest.main()
