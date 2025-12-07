"""Manager Promotion Code model for SAVING_SERVER."""

from datetime import datetime
from models.database import db

class ManagerCode(db.Model):
    """Model to store manager promotion codes for HR->Manager promotion system."""
    
    __tablename__ = 'manager_codes'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(100), unique=True, nullable=False, index=True)
    hrid = db.Column(db.String(255), nullable=False)  # HR user ID who created the code
    max_uses = db.Column(db.Integer, default=1, nullable=False)
    used_count = db.Column(db.Integer, default=0, nullable=False)
    used_by_email = db.Column(db.String(255), nullable=True)  # Email of user who used it
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    used_at = db.Column(db.DateTime(timezone=True), nullable=True)
    
    def is_valid(self):
        """Check if the code is still valid for use."""
        if not self.is_active:
            return False, "Code is inactive"
        if self.used_count >= self.max_uses:
            return False, "Code already used"
        return True, "Code is valid"
    
    def mark_as_used(self, user_email):
        """Mark the code as used by a specific user."""
        self.used_count += 1
        self.used_by_email = user_email
        self.used_at = datetime.utcnow()
        
        # Deactivate if max uses reached
        if self.used_count >= self.max_uses:
            self.is_active = False
    
    def to_dict(self):
        """Convert manager code object to dictionary."""
        return {
            'id': self.id,
            'code': self.code,
            'hrid': self.hrid,
            'max_uses': self.max_uses,
            'used_count': self.used_count,
            'used_by_email': self.used_by_email,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'used_at': self.used_at.isoformat() if self.used_at else None
        }
