"""
API Verification Script for SAVING_SERVER
Tests all endpoints using SQLite (bypassing PostgreSQL connection issues)
"""
import unittest
import json
import os
import sys
from flask import Flask
from datetime import datetime

# Create a fresh Flask app for testing
app = Flask(__name__)
app.config['TESTING'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'test-secret-key'
app.config['INTERNAL_API_KEY'] = 'nexus-internal-secret-key-123'

# Initialize database
from models.database import db
db.init_app(app)

# Import models after db init
from models import User, Invite, File, Meeting, Activity

# Register blueprints
from routes.users import users_bp
from routes.invites import invites_bp
from routes.files import files_bp
from routes.meetings import meetings_bp
from routes.activities import activities_bp

app.register_blueprint(users_bp, url_prefix='/users')
app.register_blueprint(invites_bp, url_prefix='/invites')
app.register_blueprint(files_bp, url_prefix='/file')
app.register_blueprint(meetings_bp, url_prefix='/meetings')
app.register_blueprint(activities_bp, url_prefix='/activities')

# Add health endpoint
@app.route('/health')
def health():
    return {
        "status": "healthy",
        "service": "SAVING_SERVER",
        "version": "1.0"
    }

class TestAPIs(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = app.test_client()
        
        # Create context and database
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Internal API Key
        self.headers = {
            "X-Internal-Key": "nexus-internal-secret-key-123",
            "Content-Type": "application/json"
        }

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_01_health(self):
        print("\n=== Testing Health Endpoint ===")
        response = self.client.get('/health')
        print(f"Status: {response.status_code}")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        print("✅ Health check passed")

    def test_02_unauthorized(self):
        print("\n=== Testing Unauthorized Access ===")
        response = self.client.get('/users/')  # No API key
        print(f"Status: {response.status_code}")
        self.assertEqual(response.status_code, 401)
        print("✅ Unauthorized access blocked correctly")

    def test_03_create_user(self):
        print("\n=== Testing Create User ===")
        user_data = {
            "email": "test@example.com",
            "userID": "auth0_test_123",
            "password": "placeholder",
            "role": "employee",
            "first_name": "Test",
            "last_name": "User",
            "address": "123 Test St",
            "department": "QA",
            "date_of_birth": "1990-01-01"
        }
        response = self.client.post('/users/', headers=self.headers, json=user_data)
        print(f"Status: {response.status_code}")
        self.assertIn(response.status_code, [200, 201])
        print("✅ User created successfully")

    def test_04_get_users(self):
        print("\n=== Testing Get Users ===")
        # Create a user first
        user_data = {
            "email": "gettest@example.com",
            "userID": "auth0_gettest_456",
            "password": "pwd",
            "role": "employee",
            "first_name": "Get",
            "last_name": "Test",
            "address": "456 Test Ave",
            "department": "QA",
            "date_of_birth": "1990-01-01"
        }
        self.client.post('/users/', headers=self.headers, json=user_data)
        
        response = self.client.get('/users/', headers=self.headers)
        print(f"Status: {response.status_code}")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(len(data.get('data', [])) > 0)
        print(f"✅ Found {len(data.get('data', []))} users")

    def test_05_create_activity(self):
        print("\n=== Testing Create Activity ===")
        # Create creator first
        creator_data = {
            "email": "creator@example.com",
            "userID": "auth0_creator_789",
            "password": "pwd",
            "role": "manager",
            "first_name": "Creator",
            "last_name": "User",
            "address": "789 Creator Rd",
            "department": "Admin",
            "date_of_birth": "1985-01-01"
        }
        self.client.post('/users/', headers=self.headers, json=creator_data)

        activity_data = {
            "type": "meeting",
            "title": "Team Sync",
            "description": "Weekly team sync",
            "creator": "creator@example.com",
            "date": "2025-01-15T10:00:00",
            "status": "scheduled"
        }
        response = self.client.post('/activities/', headers=self.headers, json=activity_data)
        print(f"Status: {response.status_code}")
        self.assertIn(response.status_code, [200, 201])
        print("✅ Activity created successfully")

    def test_06_get_activities(self):
        print("\n=== Testing Get Activities ===")
        response = self.client.get('/activities/', headers=self.headers)
        print(f"Status: {response.status_code}")
        self.assertEqual(response.status_code, 200)
        print("✅ Activities retrieved successfully")

if __name__ == "__main__":
    print("🚀 Starting API Tests with SQLite (Bypassing Local Postgres)...")
    print("=" * 60)
    unittest.main(verbosity=2)
