"""User model for SAVING_SERVER."""

from datetime import datetime
from models.database import db

class User(db.Model):
    """User model matching SAVING_SERVER specification."""
    
    __tablename__ = 'users'
    
    # Primary fields
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    user_id = db.Column(db.String(255), unique=True, nullable=False, index=True) # From Auth Provider
    password = db.Column(db.String(255), nullable=True) # Placeholder
    
    # Personal information
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date)
    address = db.Column(db.Text)
    
    # Work information
    role = db.Column(db.String(50), nullable=False) # 'hr', 'manager', 'employee', 'guest'
    department = db.Column(db.String(100))
    
    # Manager specific
    # Storing as JSON array of strings
    employees_list = db.Column(db.JSON, default=[])
    
    # Metadata
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    invites = db.relationship('Invite', backref='manager', lazy=True)
    files = db.relationship('File', backref='uploader', lazy=True)

    def to_dict(self):
        """Convert user object to dictionary."""
        return {
            'id': self.id,
            'email': self.email,
            'userID': self.user_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role,
            'department': self.department,
            'address': self.address,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'employeesList': self.employees_list,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
