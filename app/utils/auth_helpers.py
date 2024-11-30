from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import jsonify
from functools import wraps

def role_required(allowed_roles):
    """Decorator to check if the user's role is in allowed_roles."""
    def decorator(func):
        @wraps(func)  # Preserve the original function name and metadata
        @jwt_required()
        def wrapper(*args, **kwargs):
            user = get_jwt_identity()  # Extract user identity from JWT
            if user['role'] not in allowed_roles:
                return jsonify({"message": "Access forbidden: insufficient role"}), 403
            return func(*args, **kwargs)
        return wrapper
    return decorator
