"""File model for SAVING_SERVER."""

from datetime import datetime
from models.database import db

class File(db.Model):
    """File metadata model."""
    
    __tablename__ = 'files'
    
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.String(255), unique=True, nullable=False, index=True)
    filename = db.Column(db.String(255), nullable=False, index=True)
    original_filename = db.Column(db.String(255), nullable=False)
    size = db.Column(db.BigInteger, nullable=False)
    content_type = db.Column(db.String(100))
    
    uploaded_by = db.Column(db.String(255), db.ForeignKey('users.email'), nullable=False)
    uploaded_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    
    file_path = db.Column(db.Text, nullable=False)
    is_deleted = db.Column(db.Boolean, default=False)
    download_count = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            'file_id': self.file_id,
            'filename': self.filename,
            'size': self.size,
            'content_type': self.content_type,
            'uploaded_by': self.uploaded_by,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None
        }
