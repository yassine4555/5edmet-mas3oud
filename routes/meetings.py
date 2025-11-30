"""Meeting routes for SAVING_SERVER."""

import os
from flask import Blueprint, request, jsonify, current_app, send_file
from models import db, Meeting, User
from utils.security import require_api_key
from sqlalchemy.exc import IntegrityError
from datetime import datetime

meetings_bp = Blueprint('meetings', __name__)

@meetings_bp.route('/', methods=['POST'])
@require_api_key
def create_meeting():
    """Create a new meeting."""
    data = request.get_json()
    
    required_fields = ['title', 'created_by']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 422
    
    # Verify creator exists
    creator = User.query.filter_by(email=data['created_by']).first()
    if not creator:
        return jsonify({"error": "Creator user not found"}), 404
    
    try:
        new_meeting = Meeting(
            title=data['title'],
            object=data.get('object', ''),
            description=data.get('description', ''),
            created_by=data['created_by'],
            password=data.get('password', ''),
            invited_employees_list=data.get('invited_employees', [])
        )
        
        db.session.add(new_meeting)
        db.session.commit()
        
        # Create log directory if it doesn't exist
        log_dir = os.path.join(current_app.config.get('UPLOAD_FOLDER', './storage'), 'meeting_logs')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Set log path
        log_filename = f"meeting_{new_meeting.meeting_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        log_path = os.path.join(log_dir, log_filename)
        new_meeting.log_path = log_path
        
        # Create initial log file
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(f"Meeting Log: {new_meeting.title}\n")
            f.write(f"Meeting ID: {new_meeting.meeting_id}\n")
            f.write(f"Created By: {new_meeting.created_by}\n")
            f.write(f"Created At: {new_meeting.created_at}\n")
            f.write(f"Invitation Link: {new_meeting.invitation_link}\n")
            f.write("=" * 80 + "\n\n")
        
        db.session.commit()
        
        return jsonify(new_meeting.to_dict_with_password()), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating meeting: {e}")
        return jsonify({"error": str(e)}), 500


@meetings_bp.route('/', methods=['GET'])
@require_api_key
def get_meetings():
    """Get all meetings or filter by user."""
    user_email = request.args.get('user_email')
    is_active = request.args.get('is_active')
    
    query = Meeting.query
    
    if user_email:
        # Get meetings created by user or where user is invited
        query = query.filter(
            db.or_(
                Meeting.created_by == user_email,
                Meeting.invited_employees_list.contains([user_email])
            )
        )
    
    if is_active is not None:
        query = query.filter_by(is_active=(is_active.lower() == 'true'))
    
    meetings = query.order_by(Meeting.created_at.desc()).all()
    return jsonify({"data": [meeting.to_dict() for meeting in meetings]}), 200


@meetings_bp.route('/<meeting_id>', methods=['GET'])
@require_api_key
def get_meeting(meeting_id):
    """Get a specific meeting by ID."""
    meeting = Meeting.query.filter_by(meeting_id=meeting_id).first()
    
    if not meeting:
        return jsonify({"error": "Meeting not found"}), 404
    
    return jsonify(meeting.to_dict()), 200


@meetings_bp.route('/<meeting_id>', methods=['PUT'])
@require_api_key
def update_meeting(meeting_id):
    """Update a meeting."""
    meeting = Meeting.query.filter_by(meeting_id=meeting_id).first()
    
    if not meeting:
        return jsonify({"error": "Meeting not found"}), 404
    
    data = request.get_json()
    
    # Update allowed fields
    if 'title' in data:
        meeting.title = data['title']
    if 'object' in data:
        meeting.object = data['object']
    if 'description' in data:
        meeting.description = data['description']
    if 'password' in data:
        meeting.password = data['password']
    if 'invited_employees' in data:
        meeting.invited_employees_list = data['invited_employees']
    if 'is_active' in data:
        meeting.is_active = data['is_active']
    
    try:
        db.session.commit()
        return jsonify(meeting.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@meetings_bp.route('/<meeting_id>/start', methods=['POST'])
@require_api_key
def start_meeting(meeting_id):
    """Mark meeting as started."""
    meeting = Meeting.query.filter_by(meeting_id=meeting_id).first()
    
    if not meeting:
        return jsonify({"error": "Meeting not found"}), 404
    
    meeting.started_at = datetime.utcnow()
    
    # Log the start
    if meeting.log_path and os.path.exists(meeting.log_path):
        with open(meeting.log_path, 'a', encoding='utf-8') as f:
            f.write(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Meeting started\n")
    
    db.session.commit()
    return jsonify(meeting.to_dict()), 200


@meetings_bp.route('/<meeting_id>/end', methods=['POST'])
@require_api_key
def end_meeting(meeting_id):
    """Mark meeting as ended."""
    meeting = Meeting.query.filter_by(meeting_id=meeting_id).first()
    
    if not meeting:
        return jsonify({"error": "Meeting not found"}), 404
    
    meeting.ended_at = datetime.utcnow()
    meeting.is_active = False
    
    # Log the end
    if meeting.log_path and os.path.exists(meeting.log_path):
        with open(meeting.log_path, 'a', encoding='utf-8') as f:
            f.write(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Meeting ended\n")
            if meeting.started_at:
                duration = meeting.ended_at - meeting.started_at
                f.write(f"Duration: {duration}\n")
    
    db.session.commit()
    return jsonify(meeting.to_dict()), 200


@meetings_bp.route('/<meeting_id>/log', methods=['POST'])
@require_api_key
def append_meeting_log(meeting_id):
    """Append log entry to meeting log file."""
    meeting = Meeting.query.filter_by(meeting_id=meeting_id).first()
    
    if not meeting:
        return jsonify({"error": "Meeting not found"}), 404
    
    data = request.get_json()
    log_entry = data.get('log_entry', '')
    
    if not log_entry:
        return jsonify({"error": "log_entry is required"}), 422
    
    if not meeting.log_path:
        return jsonify({"error": "Meeting has no log path"}), 400
    
    try:
        # Ensure log directory exists
        log_dir = os.path.dirname(meeting.log_path)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Append to log file
        with open(meeting.log_path, 'a', encoding='utf-8') as f:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"[{timestamp}] {log_entry}\n")
        
        return jsonify({"success": True, "message": "Log entry added"}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@meetings_bp.route('/<meeting_id>/log', methods=['GET'])
@require_api_key
def get_meeting_log(meeting_id):
    """Get meeting log file content or download."""
    meeting = Meeting.query.filter_by(meeting_id=meeting_id).first()
    
    if not meeting:
        return jsonify({"error": "Meeting not found"}), 404
    
    if not meeting.log_path or not os.path.exists(meeting.log_path):
        return jsonify({"error": "Log file not found"}), 404
    
    # Check if download is requested
    download = request.args.get('download', 'false').lower() == 'true'
    
    if download:
        return send_file(
            meeting.log_path,
            as_attachment=True,
            download_name=f"meeting_{meeting.meeting_id}_log.txt"
        )
    else:
        # Return log content as JSON
        try:
            with open(meeting.log_path, 'r', encoding='utf-8') as f:
                log_content = f.read()
            return jsonify({
                "meeting_id": meeting_id,
                "log_path": meeting.log_path,
                "log_content": log_content
            }), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500


@meetings_bp.route('/<meeting_id>', methods=['DELETE'])
@require_api_key
def delete_meeting(meeting_id):
    """Delete a meeting (soft delete by marking inactive)."""
    meeting = Meeting.query.filter_by(meeting_id=meeting_id).first()
    
    if not meeting:
        return jsonify({"error": "Meeting not found"}), 404
    
    # Soft delete
    meeting.is_active = False
    
    # Log deletion
    if meeting.log_path and os.path.exists(meeting.log_path):
        with open(meeting.log_path, 'a', encoding='utf-8') as f:
            f.write(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Meeting deleted (soft delete)\n")
    
    db.session.commit()
    return jsonify({"success": True, "message": "Meeting deleted"}), 200
