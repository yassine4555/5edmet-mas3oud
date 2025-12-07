from flask import Blueprint, request, jsonify
from models import db, Invite, User
from utils.security import require_api_key
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError

invites_bp = Blueprint('invites', __name__)

@invites_bp.route('/', methods=['POST'])
@require_api_key
def create_invite():
    data = request.get_json()
    
    if 'manager_id' not in data or 'code' not in data:
        return jsonify({"error": "Missing manager_id or code"}), 422
        
    # Verify manager exists
    manager = User.query.filter_by(user_id=data['manager_id']).first()
    if not manager:
        return jsonify({"error": "Manager not found"}), 404
        
    # Verify role (optional, but good practice)
    if manager.role.lower() not in ['manager', 'hr']:
         return jsonify({"error": "User is not authorized to create invites"}), 403

    try:
        new_invite = Invite(
            manager_id=data['manager_id'],
            code=data['code'],
            max_uses=data.get('max_uses', 1),
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        
        db.session.add(new_invite)
        db.session.commit()
        
        return jsonify(new_invite.to_dict()), 201
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Code already exists"}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@invites_bp.route('/<code>', methods=['GET'])
@require_api_key
def get_invite_by_code(code):
    """
    Get invite details by code.
    
    Example response:
    {
        "id": 1,
        "manager_id": "auth0_manager_123",
        "code": "hf9ou",
        "max_uses": 5,
        "used_count": 0,
        "expires_at": "2025-12-14T10:30:00Z",
        "is_active": true,
        "created_at": "2025-12-07T10:30:00Z"
    }
    """
    try:
        invite = Invite.query.filter_by(code=code).first()
        
        if not invite:
            return jsonify({
                "success": False,
                "error": "Invite code not found"
            }), 404
        
        return jsonify({
            "success": True,
            "data": invite.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
