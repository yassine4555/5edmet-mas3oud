"""Manager Code routes for SAVING_SERVER."""

from flask import Blueprint, request, jsonify
from models import db, ManagerCode, User
from utils.security import require_api_key
from sqlalchemy.exc import IntegrityError

manager_codes_bp = Blueprint('manager_codes', __name__)

@manager_codes_bp.route('/becameManagerCode', methods=['POST'])
@require_api_key
def save_manager_code():
    """
    Save a manager promotion code.
    
    Request Body:
    {
        "hrid": "string",
        "code": "string",
        "max_uses": 1
    }
    
    Response:
    {
        "success": true,
        "message": "Code saved successfully"
    }
    """
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['hrid', 'code']
    for field in required_fields:
        if field not in data:
            return jsonify({
                "success": False,
                "error": f"Missing required field: {field}"
            }), 422
    
    try:
        # Check if code already exists
        existing_code = ManagerCode.query.filter_by(code=data['code']).first()
        if existing_code:
            return jsonify({
                "success": False,
                "error": "Code already exists"
            }), 409
        
        # Create new manager code
        new_code = ManagerCode(
            code=data['code'],
            hrid=data['hrid'],
            max_uses=data.get('max_uses', 1)
        )
        
        db.session.add(new_code)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Code saved successfully",
            "data": new_code.to_dict()
        }), 201
        
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": "Database integrity error"
        }), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@manager_codes_bp.route('/validateBecameManagerCode', methods=['POST'])
@require_api_key
def validate_manager_code():
    """
    Validate and use a manager promotion code.
    
    Request Body:
    {
        "code": "string",
        "userMail": "string"
    }
    
    Success Response:
    {
        "valid": true,
        "hrid": "string"
    }
    
    Error Response:
    {
        "valid": false,
        "error": "Code invalid/expired/already used"
    }
    """
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['code', 'userMail']
    for field in required_fields:
        if field not in data:
            return jsonify({
                "valid": False,
                "error": f"Missing required field: {field}"
            }), 422
    
    try:
        # Find the code
        manager_code = ManagerCode.query.filter_by(code=data['code']).first()
        
        if not manager_code:
            return jsonify({
                "valid": False,
                "error": "Code not found"
            }), 404
        
        # Check if code is valid
        is_valid, message = manager_code.is_valid()
        if not is_valid:
            return jsonify({
                "valid": False,
                "error": message
            }), 400
        
        # Verify user exists
        user = User.query.filter_by(email=data['userMail']).first()
        if not user:
            return jsonify({
                "valid": False,
                "error": "User not found"
            }), 404
        
        # Mark code as used
        manager_code.mark_as_used(data['userMail'])
        
        # Promote user to manager
        user.role = 'manager'
        
        db.session.commit()
        
        return jsonify({
            "valid": True,
            "hrid": manager_code.hrid,
            "message": "User promoted to manager successfully",
            "user": user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "valid": False,
            "error": str(e)
        }), 500


@manager_codes_bp.route('/becameManagerCode/<code>', methods=['GET'])
@require_api_key
def get_manager_code(code):
    """
    Get information about a specific manager code.
    
    Response:
    {
        "success": true,
        "data": { ... }
    }
    """
    try:
        manager_code = ManagerCode.query.filter_by(code=code).first()
        
        if not manager_code:
            return jsonify({
                "success": False,
                "error": "Code not found"
            }), 404
        
        return jsonify({
            "success": True,
            "data": manager_code.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@manager_codes_bp.route('/becameManagerCode', methods=['GET'])
@require_api_key
def list_manager_codes():
    """
    List all manager promotion codes (optionally filtered by hrid).
    
    Query Parameters:
    - hrid: Filter by HR ID
    - active_only: Show only active codes (default: false)
    
    Response:
    {
        "success": true,
        "data": [ ... ]
    }
    """
    try:
        query = ManagerCode.query
        
        # Filter by hrid if provided
        hrid = request.args.get('hrid')
        if hrid:
            query = query.filter_by(hrid=hrid)
        
        # Filter by active status
        active_only = request.args.get('active_only', 'false').lower() == 'true'
        if active_only:
            query = query.filter_by(is_active=True)
        
        codes = query.all()
        
        return jsonify({
            "success": True,
            "data": [code.to_dict() for code in codes]
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
