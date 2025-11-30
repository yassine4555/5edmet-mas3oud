from functools import wraps
from flask import request, jsonify, current_app

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-Internal-Key')
        internal_key = current_app.config.get('INTERNAL_API_KEY')
        
        if not api_key or api_key != internal_key:
            return jsonify({"error": "Unauthorized", "code": "UNAUTHORIZED"}), 401
            
        return f(*args, **kwargs)
    return decorated_function
