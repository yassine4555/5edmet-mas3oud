from flask import Blueprint, request, jsonify
from models import db, User
from utils.security import require_api_key
from sqlalchemy.exc import IntegrityError

users_bp = Blueprint('users', __name__)

@users_bp.route('/', methods=['POST'])
@require_api_key
def create_user():
    data = request.get_json()
    
    required_fields = ['email', 'userID', 'role', 'first_name', 'last_name']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 422
    
    # Validate role
    valid_roles = ['hr', 'manager', 'employee', 'guest']
    if data['role'].lower() not in valid_roles:
        return jsonify({
            "error": f"Invalid role: {data['role']}",
            "valid_roles": valid_roles
        }), 400
            
    try:
        new_user = User(
            email=data['email'],
            user_id=data['userID'],
            password=data.get('password', 'placeholder'),
            role=data['role'].lower(),
            first_name=data['first_name'],
            last_name=data['last_name'],
            address=data.get('address'),
            department=data.get('department'),
            # Handle date_of_birth parsing if needed, assuming string YYYY-MM-DD or similar
            # For simplicity in this step, we might need to parse it if it's a string
        )
        
        # Handle date parsing
        if 'date_of_birth' in data and data['date_of_birth']:
            from datetime import datetime
            try:
                new_user.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
            except ValueError:
                pass # Or return error

        db.session.add(new_user)
        db.session.commit()
        
        return jsonify(new_user.to_dict()), 201
        
    except IntegrityError as e:
        db.session.rollback()
        print(e)
        return jsonify({"error": "Email or UserID already exists"}), 409
    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({"error": str(e)}), 500

@users_bp.route('/', methods=['GET'])
@require_api_key
def get_users():
    users = User.query.all()
    return jsonify({"data": [user.to_dict() for user in users]}), 200


@users_bp.route('/<user_id>', methods=['PUT', 'PATCH'])
@require_api_key
def update_user(user_id):
    """Update user information by userID or email."""
    data = request.get_json()
    print("user id = ",user_id)
    try:
        # Find user by userID or email
        user = User.query.filter(
           (User.email == user_id)
        ).first()
        
        if not user:
            return jsonify({
                "success": False,
                "error": "User not found"
            }), 404
        
        # Update allowed fields
        updatable_fields = [
            'email', 'first_name', 'last_name', 'role', 
            'department', 'address', 'date_of_birth', 'password'
        ]
        
        updated_fields = []
        for field in updatable_fields:
            if field in data:
                setattr(user, field, data[field])
                updated_fields.append(field)
        
        # Handle employees_list separately (expecting a list of employee emails/IDs)
        if 'employees_list' in data or 'employeesList' in data:
            employees_data = data.get('employees_list') or data.get('employeesList')
            
            # Validate that it's a list
            if not isinstance(employees_data, list):
                return jsonify({
                    "success": False,
                    "error": "employees_list must be an array/list"
                }), 400
            
            # Set the employees list
            user.employees_list = employees_data
            updated_fields.append('employees_list')
        
        if not updated_fields:
            return jsonify({
                "success": False,
                "error": "No valid fields to update"
            }), 400
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"User updated successfully. Updated fields: {', '.join(updated_fields)}",
            "data": user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@users_bp.route('/<email>/teammates', methods=['GET'])
@require_api_key
def get_teammates(email):
    """
    Get all teammates of an employee.
    
    This endpoint finds the manager(s) who have this employee in their employees_list
    and returns all other employees in that list (excluding the requesting employee).
    
    URL Parameters:
        email (string): The email of the employee
        
    Query Parameters:
        include_details (bool): If true, returns full user objects instead of just emails
        include_manager (bool): If true, includes manager info in response
    
    Response:
    {
        "success": true,
        "employee": "employee@company.com",
        "manager": { ... },  // Only if include_manager=true
        "teammates": ["teammate1@company.com", ...] or [{ user objects }],
        "teammates_count": 2
    }
    """
    try:
        # Verify the employee exists
        employee = User.query.filter_by(email=email).first()
        if not employee:
            return jsonify({
                "success": False,
                "error": "Employee not found"
            }), 404
        
        # Find manager(s) who have this employee in their employees_list
        # We need to search in JSON array - using PostgreSQL JSON contains
        managers = User.query.filter(
            User.employees_list.contains([email])
        ).all()
        
        if not managers:
            return jsonify({
                "success": True,
                "employee": email,
                "message": "No manager found for this employee",
                "manager": None,
                "teammates": [],
                "teammates_count": 0
            }), 200
        
        # Get query parameters
        include_details = request.args.get('include_details', 'false').lower() == 'true'
        include_manager = request.args.get('include_manager', 'false').lower() == 'true'
        
        # Collect all teammates from all managers (in case employee has multiple managers)
        all_teammates = set()
        managers_info = []
        
        for manager in managers:
            if manager.employees_list:
                # Add all employees except the requesting employee
                for teammate_email in manager.employees_list:
                    if teammate_email != email:
                        all_teammates.add(teammate_email)
            
            if include_manager:
                managers_info.append({
                    "email": manager.email,
                    "first_name": manager.first_name,
                    "last_name": manager.last_name,
                    "department": manager.department
                })
        
        # Convert to list
        teammates_list = list(all_teammates)
        
        # If include_details is true, fetch full user objects for each teammate
        if include_details and teammates_list:
            teammates_users = User.query.filter(User.email.in_(teammates_list)).all()
            teammates_response = [user.to_dict() for user in teammates_users]
        else:
            teammates_response = teammates_list
        
        response = {
            "success": True,
            "employee": email,
            "teammates": teammates_response,
            "teammates_count": len(teammates_list)
        }
        
        # Include manager info if requested
        if include_manager:
            response["manager"] = managers_info[0] if len(managers_info) == 1 else managers_info
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@users_bp.route('/<email>/team', methods=['GET'])
@require_api_key
def get_full_team(email):
    """
    Get the full team info including manager and all teammates.
    
    URL Parameters:
        email (string): The email of the employee
    
    Response:
    {
        "success": true,
        "employee": { employee details },
        "manager": { manager details },
        "teammates": [{ teammate details }, ...],
        "team_size": 5
    }
    """
    try:
        # Verify the employee exists
        employee = User.query.filter_by(email=email).first()
        if not employee:
            return jsonify({
                "success": False,
                "error": "Employee not found"
            }), 404
        
        # Find manager who has this employee in their employees_list
        manager = User.query.filter(
            User.employees_list.contains([email])
        ).first()
        
        if not manager:
            return jsonify({
                "success": True,
                "employee": employee.to_dict(),
                "manager": None,
                "teammates": [],
                "team_size": 1,
                "message": "No manager found for this employee"
            }), 200
        
        # Get all teammates (excluding self)
        teammates_emails = [e for e in (manager.employees_list or []) if e != email]
        
        # Fetch full user objects for teammates
        teammates = []
        if teammates_emails:
            teammates_users = User.query.filter(User.email.in_(teammates_emails)).all()
            teammates = [user.to_dict() for user in teammates_users]
        
        return jsonify({
            "success": True,
            "employee": employee.to_dict(),
            "manager": {
                "email": manager.email,
                "userID": manager.user_id,
                "first_name": manager.first_name,
                "last_name": manager.last_name,
                "department": manager.department,
                "role": manager.role
            },
            "teammates": teammates,
            "team_size": len(teammates) + 1  # Including the employee
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500