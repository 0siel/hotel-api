
from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps
from flask import jsonify
import json

def role_required(allowed_roles):
    """Decorator to check if the user's role is in allowed_roles."""
    def decorator(func):
        @wraps(func)
        @jwt_required()
        def wrapper(*args, **kwargs):
            # Deserialize the identity string into a dictionary
            user = json.loads(get_jwt_identity())
            if user["role"] not in allowed_roles:
                return jsonify({"message": "Access forbidden: insufficient role"}), 403
            return func(*args, **kwargs)
        return wrapper
    return decorator