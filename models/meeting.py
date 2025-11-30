"""Meeting model for SAVING_SERVER."""

from datetime import datetime
from models.database import db
import uuid

class Meeting(db.Model):
    """Meeting model with log path support."""
    
    __tablename__ = 'meetings'
    
    id = db.Column(db.Integer, primary_key=True)
    meeting_id = db.Column(db.String(255), unique=True, nullable=False, index=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(255), nullable=False)
    object = db.Column(db.String(255))
    description = db.Column(db.Text)
    invitation_link = db.Column(db.String(500))
    password = db.Column(db.String(255))
    
    # Log storage
    log_path = db.Column(db.Text)
    
    # Invited employees stored as JSON array of user IDs/emails
    invited_employees_list = db.Column(db.JSON, default=[])
    
    # Creator information
    created_by = db.Column(db.String(255), db.ForeignKey('users.email'), nullable=False)
    
    # Metadata
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Meeting status
    is_active = db.Column(db.Boolean, default=True)
    started_at = db.Column(db.DateTime(timezone=True))
    ended_at = db.Column(db.DateTime(timezone=True))
    
    # Relationships
    creator = db.relationship('User', backref='meetings_created', lazy=True)

    def __init__(self, **kwargs):
        super(Meeting, self).__init__(**kwargs)
        if not self.meeting_id:
            self.meeting_id = str(uuid.uuid4())
        if not self.invitation_link:
            self.invitation_link = f"http://localhost:7053/room/{self.meeting_id}"

    def to_dict(self):
        """Convert meeting object to dictionary."""
        return {
            'id': self.id,
            'meeting_id': self.meeting_id,
            'title': self.title,
            'object': self.object,
            'description': self.description,
            'invitation_link': self.invitation_link,
            'log_path': self.log_path,
            'invited_employees_list': self.invited_employees_list,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
            'has_password': bool(self.password)
        }
    
    def to_dict_with_password(self):
        """Convert meeting object to dictionary including password (for creator only)."""
        data = self.to_dict()
        data['password'] = self.password
        return data
