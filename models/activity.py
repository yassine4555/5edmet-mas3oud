"""Activity model for SAVING_SERVER."""

from datetime import datetime
from models.database import db
import uuid


class Activity(db.Model):
    """Activity model for tracking team activities/events."""
    
    __tablename__ = 'activities'
    
    # Primary fields
    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.String(255), unique=True, nullable=False, index=True, default=lambda: str(uuid.uuid4()))
    
    # Activity information
    date = db.Column(db.DateTime(timezone=True), nullable=False)
    type = db.Column(db.String(100), nullable=False)  # e.g., 'meeting', 'training', 'team_building', 'workshop', etc.
    title = db.Column(db.String(255))
    description = db.Column(db.Text)
    
    # Creator information
    creator = db.Column(db.String(255), db.ForeignKey('users.email'), nullable=False)
    
    # Participants - stored as JSON array of employee emails
    employees_joined = db.Column(db.JSON, default=[])
    
    # Status
    status = db.Column(db.String(50), default='scheduled')  # 'scheduled', 'ongoing', 'completed', 'cancelled'
    
    # Metadata
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator_user = db.relationship('User', backref='activities_created', lazy=True)

    def __init__(self, **kwargs):
        super(Activity, self).__init__(**kwargs)
        if not self.activity_id:
            self.activity_id = str(uuid.uuid4())

    def to_dict(self):
        """Convert activity object to dictionary."""
        return {
            'id': self.id,
            'activity_id': self.activity_id,
            'date': self.date.isoformat() if self.date else None,
            'type': self.type,
            'title': self.title,
            'description': self.description,
            'creator': self.creator,
            'employees_joined': self.employees_joined,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def add_employee(self, email):
        """Add an employee to the activity."""
        if self.employees_joined is None:
            self.employees_joined = []
        if email not in self.employees_joined:
            self.employees_joined = self.employees_joined + [email]
            return True
        return False

    def remove_employee(self, email):
        """Remove an employee from the activity."""
        if self.employees_joined and email in self.employees_joined:
            self.employees_joined = [e for e in self.employees_joined if e != email]
            return True
        return False
