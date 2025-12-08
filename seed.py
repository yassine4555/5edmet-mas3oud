from app import app, db
from models import User, Invite, File, Activity, Meeting

def seed_data():
    with app.app_context():
        print("Seeding data...")
        
        # Create tables if they don't exist
        db.create_all()
        
        # Check if data exists
        if User.query.first():
            print("Data already exists.")
            return

        # Users
        admin = User(
            email='admin@example.com',
            user_id='auth0_admin_123',
            first_name='Admin',
            last_name='User',
            role='hr',
            department='Administration',
            address='123 Admin St',
            date_of_birth=datetime(1980, 1, 1)
        )
        
        manager = User(
            email='manager@example.com',
            user_id='auth0_manager_456',
            first_name='Jane',
            last_name='Manager',
            role='manager',
            department='Engineering',
            address='456 Manager Ave',
            date_of_birth=datetime(1985, 5, 15),
            employees_list=['employee@example.com']
        )
        
        employee = User(
            email='employee@example.com',
            user_id='auth0_employee_789',
            first_name='John',
            last_name='Doe',
            role='employee',
            department='Engineering',
            address='789 Worker Rd',
            date_of_birth=datetime(1990, 8, 20)
        )
        
        db.session.add_all([admin, manager, employee])
        db.session.commit()
        
        # Invites
        invite = Invite(
            manager_id='auth0_manager_456',
            code='TESTCODE',
            max_uses=5,
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        db.session.add(invite)
        
        # Files
        file = File(
            file_id='file_123456789',
            filename='welcome_packet.pdf',
            original_filename='Welcome Packet 2025.pdf',
            size=102400,
            content_type='application/pdf',
            uploaded_by='admin@example.com',
            file_path='/storage/files/welcome_packet.pdf'
        )
        db.session.add(file)
        
        # Activity (Seed for verification)
        activity = Activity(
            type='system',
            title='Database Initialized',
            description='Initial seed data created',
            creator='admin@example.com',
            date=datetime.utcnow(),
            status='completed'
        )
        db.session.add(activity)
        
        db.session.commit()
        print("Seeding completed!")

if __name__ == '__main__':
    seed_data()
