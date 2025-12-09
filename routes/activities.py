"""Activity routes for SAVING_SERVER."""

from flask import Blueprint, request, jsonify
from models import db, Activity, User
from utils.security import require_api_key
from sqlalchemy.exc import IntegrityError
from datetime import datetime

activities_bp = Blueprint('activities', __name__)


@activities_bp.route('/', methods=['POST'])
@require_api_key
def create_activity():
    """Create a new activity."""
    data = request.get_json()
    
    # Required fields validation
    required_fields = ['date', 'creator', 'type']
    for field in required_fields:
        if field not in data:
            return jsonify({
                "success": False,
                "error": f"Missing required field: {field}"
            }), 422
    
    # Verify creator exists
    creator = User.query.filter_by(email=data['creator']).first()
    if not creator:
        return jsonify({
            "success": False,
            "error": "Creator user not found"
        }), 404
    
    # Validate activity type
    #valid_types = ['meeting', 'training', 'team_building', 'workshop', 'presentation', 'review', 'other']
    #if data['type'].lower() not in valid_types:
    #    return jsonify({
    #        "success": False,
    #        "error": f"Invalid activity type: {data['type']}",
    #        "valid_types": valid_types
    #    }), 400
    
    try:
        # Parse date
        activity_date = None
        if isinstance(data['date'], str):
            try:
                # Try ISO format first
                activity_date = datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
            except ValueError:
                try:
                    # Try common date format
                    activity_date = datetime.strptime(data['date'], '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    try:
                        # Try date only
                        activity_date = datetime.strptime(data['date'], '%Y-%m-%d')
                    except ValueError:
                        return jsonify({
                            "success": False,
                            "error": "Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS) or YYYY-MM-DD"
                        }), 400
        else:
            activity_date = data['date']
        
        new_activity = Activity(
            date=activity_date,
            type=data['type'].lower(),
            creator=data['creator'],
            title=data.get('title', ''),
            description=data.get('description', ''),
            employees_joined=data.get('employees_joined', []),
            status=data.get('status', 'scheduled')
        )
        
        db.session.add(new_activity)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Activity created successfully",
            "data": new_activity.to_dict()
        }), 201
        
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": "Activity creation failed - integrity error"
        }), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@activities_bp.route('/', methods=['GET'])
@require_api_key
def get_activities():
    """
    Get all activities with optional filtering.
    
    Query Parameters:
        - creator: Filter by creator email
        - type: Filter by activity type
        - status: Filter by status
        - employee: Filter activities where this employee has joined
        - from_date: Filter activities from this date (YYYY-MM-DD)
        - to_date: Filter activities until this date (YYYY-MM-DD)
    """
    query = Activity.query
    
    # Filter by creator
    creator = request.args.get('creator')
    if creator:
        query = query.filter(Activity.creator == creator)
    
    # Filter by type
    activity_type = request.args.get('type')
    if activity_type:
        query = query.filter(Activity.type == activity_type.lower())
    
    # Filter by status
    status = request.args.get('status')
    if status:
        query = query.filter(Activity.status == status.lower())
    
    # Filter by date range
    from_date = request.args.get('from_date')
    if from_date:
        try:
            from_dt = datetime.strptime(from_date, '%Y-%m-%d')
            query = query.filter(Activity.date >= from_dt)
        except ValueError:
            pass
    
    to_date = request.args.get('to_date')
    if to_date:
        try:
            to_dt = datetime.strptime(to_date, '%Y-%m-%d')
            query = query.filter(Activity.date <= to_dt)
        except ValueError:
            pass
    
    # Get activities from database first
    activities = query.order_by(Activity.date.desc()).all()
    
    # Filter by employee participation (in Python to avoid JSON query issues)
    employee = request.args.get('employee')
    if employee:
        activities = [
            activity for activity in activities 
            if (activity.employees_joined and 
                isinstance(activity.employees_joined, list) and 
                employee in activity.employees_joined)
        ]
    
    return jsonify({
        "success": True,
        "count": len(activities),
        "data": [activity.to_dict() for activity in activities]
    }), 200


@activities_bp.route('/<activity_id>', methods=['GET'])
@require_api_key
def get_activity(activity_id):
    """Get a specific activity by activity_id or id."""
    # Try to find by activity_id first (UUID), then by numeric id
    activity = Activity.query.filter_by(activity_id=activity_id).first()
    
    if not activity:
        # Try numeric ID
        try:
            numeric_id = int(activity_id)
            activity = Activity.query.get(numeric_id)
        except ValueError:
            pass
    
    if not activity:
        return jsonify({
            "success": False,
            "error": "Activity not found"
        }), 404
    
    return jsonify({
        "success": True,
        "data": activity.to_dict()
    }), 200


@activities_bp.route('/<activity_id>', methods=['PUT', 'PATCH'])
@require_api_key
def update_activity(activity_id):
    """Update an activity."""
    # Try to find by activity_id first (UUID), then by numeric id
    activity = Activity.query.filter_by(activity_id=activity_id).first()
    
    if not activity:
        try:
            numeric_id = int(activity_id)
            activity = Activity.query.get(numeric_id)
        except ValueError:
            pass
    
    if not activity:
        return jsonify({
            "success": False,
            "error": "Activity not found"
        }), 404
    
    data = request.get_json()
    
    # Update allowed fields
    updated_fields = []
    
    if 'title' in data:
        activity.title = data['title']
        updated_fields.append('title')
    
    if 'description' in data:
        activity.description = data['description']
        updated_fields.append('description')
    
    if 'type' in data:
        valid_types = ['meeting', 'training', 'team_building', 'workshop', 'presentation', 'review', 'other']
        if data['type'].lower() in valid_types:
            activity.type = data['type'].lower()
            updated_fields.append('type')
        else:
            return jsonify({
                "success": False,
                "error": f"Invalid activity type: {data['type']}",
                "valid_types": valid_types
            }), 400
    
    if 'date' in data:
        try:
            if isinstance(data['date'], str):
                activity.date = datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
            else:
                activity.date = data['date']
            updated_fields.append('date')
        except ValueError:
            return jsonify({
                "success": False,
                "error": "Invalid date format"
            }), 400
    
    if 'employees_joined' in data:
        if not isinstance(data['employees_joined'], list):
            return jsonify({
                "success": False,
                "error": "employees_joined must be an array"
            }), 400
        activity.employees_joined = data['employees_joined']
        updated_fields.append('employees_joined')
    
    if 'status' in data:
        valid_statuses = ['scheduled', 'ongoing', 'completed', 'cancelled']
        if data['status'].lower() in valid_statuses:
            activity.status = data['status'].lower()
            updated_fields.append('status')
        else:
            return jsonify({
                "success": False,
                "error": f"Invalid status: {data['status']}",
                "valid_statuses": valid_statuses
            }), 400
    
    if not updated_fields:
        return jsonify({
            "success": False,
            "error": "No valid fields to update"
        }), 400
    
    try:
        db.session.commit()
        return jsonify({
            "success": True,
            "message": f"Activity updated successfully. Updated fields: {', '.join(updated_fields)}",
            "data": activity.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@activities_bp.route('/<activity_id>', methods=['DELETE'])
@require_api_key
def delete_activity(activity_id):
    """Delete an activity."""
    # Try to find by activity_id first (UUID), then by numeric id
    activity = Activity.query.filter_by(activity_id=activity_id).first()
    
    if not activity:
        try:
            numeric_id = int(activity_id)
            activity = Activity.query.get(numeric_id)
        except ValueError:
            pass
    
    if not activity:
        return jsonify({
            "success": False,
            "error": "Activity not found"
        }), 404
    
    try:
        activity_data = activity.to_dict()
        db.session.delete(activity)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Activity deleted successfully",
            "deleted_activity": activity_data
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@activities_bp.route('/<activity_id>/join', methods=['POST'])
@require_api_key
def join_activity(activity_id):
    """Add an employee to an activity."""
    activity = Activity.query.filter_by(activity_id=activity_id).first()
    
    if not activity:
        try:
            numeric_id = int(activity_id)
            activity = Activity.query.get(numeric_id)
        except ValueError:
            pass
    
    if not activity:
        return jsonify({
            "success": False,
            "error": "Activity not found"
        }), 404
    
    data = request.get_json()
    
    if 'employee_email' not in data:
        return jsonify({
            "success": False,
            "error": "Missing required field: employee_email"
        }), 422
    
    employee_email = data['employee_email']
    
    # Verify employee exists
    employee = User.query.filter_by(email=employee_email).first()
    if not employee:
        return jsonify({
            "success": False,
            "error": "Employee not found"
        }), 404
    
    # Add employee to activity
    if activity.add_employee(employee_email):
        try:
            db.session.commit()
            return jsonify({
                "success": True,
                "message": f"Employee {employee_email} joined the activity",
                "data": activity.to_dict()
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    else:
        return jsonify({
            "success": False,
            "error": "Employee is already in this activity"
        }), 409


@activities_bp.route('/<activity_id>/leave', methods=['POST'])
@require_api_key
def leave_activity(activity_id):
    """Remove an employee from an activity."""
    activity = Activity.query.filter_by(activity_id=activity_id).first()
    
    if not activity:
        try:
            numeric_id = int(activity_id)
            activity = Activity.query.get(numeric_id)
        except ValueError:
            pass
    
    if not activity:
        return jsonify({
            "success": False,
            "error": "Activity not found"
        }), 404
    
    data = request.get_json()
    
    if 'employee_email' not in data:
        return jsonify({
            "success": False,
            "error": "Missing required field: employee_email"
        }), 422
    
    employee_email = data['employee_email']
    
    # Remove employee from activity
    if activity.remove_employee(employee_email):
        try:
            db.session.commit()
            return jsonify({
                "success": True,
                "message": f"Employee {employee_email} left the activity",
                "data": activity.to_dict()
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    else:
        return jsonify({
            "success": False,
            "error": "Employee is not in this activity"
        }), 404


@activities_bp.route('/<activity_id>/participants', methods=['GET'])
@require_api_key
def get_activity_participants(activity_id):
    """Get all participants of an activity with their details."""
    activity = Activity.query.filter_by(activity_id=activity_id).first()
    
    if not activity:
        try:
            numeric_id = int(activity_id)
            activity = Activity.query.get(numeric_id)
        except ValueError:
            pass
    
    if not activity:
        return jsonify({
            "success": False,
            "error": "Activity not found"
        }), 404
    
    # Get query param for including details
    include_details = request.args.get('include_details', 'false').lower() == 'true'
    
    if include_details and activity.employees_joined:
        # Fetch full user details for each participant
        participants = User.query.filter(User.email.in_(activity.employees_joined)).all()
        participants_data = [user.to_dict() for user in participants]
    else:
        participants_data = activity.employees_joined or []
    
    # Get creator details
    creator_user = User.query.filter_by(email=activity.creator).first()
    creator_data = creator_user.to_dict() if creator_user else {"email": activity.creator}
    
    return jsonify({
        "success": True,
        "activity_id": activity.activity_id,
        "title": activity.title,
        "creator": creator_data,
        "participants": participants_data,
        "participants_count": len(activity.employees_joined) if activity.employees_joined else 0
    }), 200


@activities_bp.route('/user/<email>', methods=['GET'])
@require_api_key
def get_user_activities(email):
    """
    Get all activities for a specific user.
    Returns activities created by the user and activities they've joined.
    """
    # Verify user exists
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({
            "success": False,
            "error": "User not found"
        }), 404
    
    # Get filter type
    filter_type = request.args.get('filter', 'all')  # 'all', 'created', 'joined'
    
    if filter_type == 'created':
        activities = Activity.query.filter(Activity.creator == email).order_by(Activity.date.desc()).all()
    elif filter_type == 'joined':
        # Get all activities and filter in Python for joined activities
        all_activities = Activity.query.order_by(Activity.date.desc()).all()
        activities = [
            activity for activity in all_activities 
            if (activity.employees_joined and 
                isinstance(activity.employees_joined, list) and 
                email in activity.employees_joined and 
                activity.creator != email)  # Exclude activities created by user
        ]
    else:  # 'all'
        # Get all activities and filter in Python
        all_activities = Activity.query.order_by(Activity.date.desc()).all()
        activities = [
            activity for activity in all_activities 
            if (activity.creator == email or 
                (activity.employees_joined and 
                 isinstance(activity.employees_joined, list) and 
                 email in activity.employees_joined))
        ]
    
    return jsonify({
        "success": True,
        "user": email,
        "filter": filter_type,
        "count": len(activities),
        "data": [activity.to_dict() for activity in activities]
    }), 200
