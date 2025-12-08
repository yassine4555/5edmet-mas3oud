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
    """
    Delete a meeting (soft delete by marking inactive).
    Only the creator of the meeting can delete it.
    
    Request Body:
    {
        "user_email": "creator@example.com"  // Required: email of user requesting deletion
    }
    """
    meeting = Meeting.query.filter_by(meeting_id=meeting_id).first()
    
    if not meeting:
        return jsonify({
            "success": False,
            "error": "Meeting not found"
        }), 404
    
    # Get the requesting user's email from request body
    data = request.get_json() or {}
    user_email = data.get('user_email')
    
    if not user_email:
        return jsonify({
            "success": False,
            "error": "user_email is required to delete a meeting"
        }), 422
    
    # Check if the requesting user is the creator
    if meeting.created_by != user_email:
        return jsonify({
            "success": False,
            "error": "Only the creator of the meeting can delete it",
            "created_by": meeting.created_by,
            "requested_by": user_email
        }), 403
    
    # Soft delete
    meeting.is_active = False
    
    # Log deletion
    if meeting.log_path and os.path.exists(meeting.log_path):
        with open(meeting.log_path, 'a', encoding='utf-8') as f:
            f.write(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Meeting deleted by {user_email} (soft delete)\n")
    
    db.session.commit()
    
    return jsonify({
        "success": True,
        "message": "Meeting deleted successfully",
        "meeting_id": meeting_id,
        "deleted_by": user_email
    }), 200


@meetings_bp.route('/<meeting_id>/hard-delete', methods=['DELETE'])
@require_api_key
def hard_delete_meeting(meeting_id):
    """
    Permanently delete a meeting from the database.
    Only the creator of the meeting can delete it.
    WARNING: This action is irreversible.
    
    Request Body:
    {
        "user_email": "creator@example.com",  // Required: email of user requesting deletion
        "confirm": true                        // Required: confirmation flag
    }
    """
    meeting = Meeting.query.filter_by(meeting_id=meeting_id).first()
    
    if not meeting:
        return jsonify({
            "success": False,
            "error": "Meeting not found"
        }), 404
    
    data = request.get_json() or {}
    user_email = data.get('user_email')
    confirm = data.get('confirm', False)
    
    if not user_email:
        return jsonify({
            "success": False,
            "error": "user_email is required to delete a meeting"
        }), 422
    
    if not confirm:
        return jsonify({
            "success": False,
            "error": "Please set 'confirm': true to permanently delete this meeting"
        }), 422
    
    # Check if the requesting user is the creator
    if meeting.created_by != user_email:
        return jsonify({
            "success": False,
            "error": "Only the creator of the meeting can delete it",
            "created_by": meeting.created_by,
            "requested_by": user_email
        }), 403
    
    # Store meeting info for response
    deleted_meeting_id = meeting.meeting_id
    deleted_meeting_title = meeting.title
    
    # Delete log file if exists
    if meeting.log_path and os.path.exists(meeting.log_path):
        try:
            os.remove(meeting.log_path)
        except Exception as e:
            print(f"Warning: Could not delete log file: {e}")
    
    # Hard delete from database
    db.session.delete(meeting)
    db.session.commit()
    
    return jsonify({
        "success": True,
        "message": "Meeting permanently deleted",
        "meeting_id": deleted_meeting_id,
        "title": deleted_meeting_title,
        "deleted_by": user_email
    }), 200


@meetings_bp.route('/user/<email>', methods=['GET'])
@require_api_key
def get_user_meetings(email):
    """
    Get all meetings related to a specific user.
    Returns meetings created by the user and meetings they've been invited to.
    
    Query Parameters:
        - filter: 'all' (default), 'created', 'invited'
        - is_active: 'true' or 'false' to filter by active status
        - include_details: 'true' to include creator details
    """
    # Verify user exists
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({
            "success": False,
            "error": "User not found"
        }), 404
    
    # Get filter parameters
    filter_type = request.args.get('filter', 'all')  # 'all', 'created', 'invited'
    is_active = request.args.get('is_active')
    include_details = request.args.get('include_details', 'false').lower() == 'true'
    
    # Build base query
    query = Meeting.query
    
    # Filter by active status if specified
    if is_active is not None:
        query = query.filter_by(is_active=(is_active.lower() == 'true'))
    
    if filter_type == 'created':
        # Only meetings created by this user
        meetings = query.filter(Meeting.created_by == email).order_by(Meeting.created_at.desc()).all()
    elif filter_type == 'invited':
        # Only meetings where user is invited (not created by them)
        all_meetings = query.order_by(Meeting.created_at.desc()).all()
        meetings = [
            meeting for meeting in all_meetings
            if (meeting.invited_employees_list and 
                isinstance(meeting.invited_employees_list, list) and 
                email in meeting.invited_employees_list and
                meeting.created_by != email)
        ]
    else:  # 'all'
        # Get all meetings and filter in Python to avoid JSON query issues
        all_meetings = query.order_by(Meeting.created_at.desc()).all()
        meetings = [
            meeting for meeting in all_meetings
            if (meeting.created_by == email or 
                (meeting.invited_employees_list and 
                 isinstance(meeting.invited_employees_list, list) and 
                 email in meeting.invited_employees_list))
        ]
    
    # Prepare response data
    meetings_data = []
    for meeting in meetings:
        meeting_dict = meeting.to_dict()
        
        # Add relationship type
        if meeting.created_by == email:
            meeting_dict['relationship'] = 'creator'
        else:
            meeting_dict['relationship'] = 'invited'
        
        # Optionally include creator details
        if include_details and meeting.created_by != email:
            creator = User.query.filter_by(email=meeting.created_by).first()
            if creator:
                meeting_dict['creator_details'] = {
                    "email": creator.email,
                    "first_name": creator.first_name,
                    "last_name": creator.last_name,
                    "department": creator.department
                }
        
        meetings_data.append(meeting_dict)
    
    # Calculate statistics
    created_count = sum(1 for m in meetings if m.created_by == email)
    invited_count = len(meetings) - created_count
    
    return jsonify({
        "success": True,
        "user": email,
        "filter": filter_type,
        "statistics": {
            "total": len(meetings),
            "created": created_count,
            "invited": invited_count
        },
        "data": meetings_data
    }), 200


@meetings_bp.route('/user/<email>/upcoming', methods=['GET'])
@require_api_key
def get_user_upcoming_meetings(email):
    """
    Get upcoming (active) meetings for a specific user.
    Returns only active meetings that haven't ended yet.
    """
    # Verify user exists
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({
            "success": False,
            "error": "User not found"
        }), 404
    
    # Get all active meetings
    all_meetings = Meeting.query.filter_by(is_active=True).order_by(Meeting.created_at.desc()).all()
    
    # Filter meetings related to user
    meetings = [
        meeting for meeting in all_meetings
        if (meeting.created_by == email or 
            (meeting.invited_employees_list and 
             isinstance(meeting.invited_employees_list, list) and 
             email in meeting.invited_employees_list))
    ]
    
    # Separate by status
    not_started = [m for m in meetings if m.started_at is None]
    in_progress = [m for m in meetings if m.started_at is not None and m.ended_at is None]
    
    return jsonify({
        "success": True,
        "user": email,
        "upcoming": {
            "not_started": [m.to_dict() for m in not_started],
            "in_progress": [m.to_dict() for m in in_progress]
        },
        "counts": {
            "not_started": len(not_started),
            "in_progress": len(in_progress),
            "total": len(meetings)
        }
    }), 200
