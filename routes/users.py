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
