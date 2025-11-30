"""Invite model for SAVING_SERVER."""

from datetime import datetime, timedelta
from models.database import db

class Invite(db.Model):
    """Invitation code model."""
    
    __tablename__ = 'invites'
    
    id = db.Column(db.Integer, primary_key=True)
    manager_id = db.Column(db.String(255), db.ForeignKey('users.user_id'), nullable=False)
    code = db.Column(db.String(8), unique=True, nullable=False, index=True)
    max_uses = db.Column(db.Integer, default=1, nullable=False)
    current_uses = db.Column(db.Integer, default=0, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    expires_at = db.Column(db.DateTime(timezone=True))
    
    # Storing used_by as JSON array of strings
    used_by = db.Column(db.JSON, default=[])

    def to_dict(self):
        return {
            'id': self.id,
            'manager_id': self.manager_id,
            'code': self.code,
            'max_uses': self.max_uses,
            'current_uses': self.current_uses,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }
