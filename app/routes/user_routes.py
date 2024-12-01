from flask import Blueprint, request, jsonify
from app.models import User, db
from flask_jwt_extended import create_access_token
from app.utils.auth_helpers import role_required
from flask_jwt_extended import get_jwt_identity
import json

bp = Blueprint('user_routes', __name__)

@bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user.
    - Customers can self-register without authentication.
    - Admins can register staff or admins if authenticated.
    """
    # Check if the user is logged in (optional JWT)
    current_user = None
    if request.headers.get("Authorization"):
        try:
            current_user = get_jwt_identity()
        except Exception:
            pass  # Ignore errors if the request doesn't include a valid JWT

    data = request.json
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone_number')
    password = data.get('password')
    user_type = data.get('type', 'customer')  # Default to 'customer'

    # Validate input
    if not all([name, email, phone, password]):
        return jsonify({"message": "Missing required fields"}), 400

    # Restrict non-customers if not authenticated or not admin
    if user_type in ['admin', 'staff']:
        if not current_user or current_user['role'] != 'admin':
            return jsonify({"message": "Access forbidden: Only admins can create staff or admin users"}), 403

    # Check for duplicate email
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already registered"}), 400
    
    # Check for duplicate phone number
    if User.query.filter_by(phone_number=phone).first():
        return jsonify({"message": "Phone number already registered"}), 400

    # Create the user
    user = User(name=name, email=email, phone_number=phone, type=user_type)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": f"{user_type.capitalize()} user registered successfully"}), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"message": "Invalid credentials"}), 401

    # Serialize the dictionary to a string for the identity field
    token = create_access_token(identity=json.dumps({"id": user.id, "role": user.type}))
    return jsonify({"access_token": token}), 200

@bp.route('/', methods=['GET'])
@role_required(['admin'])
def list_users():
    """List all users (Admin Only)."""
    users = User.query.all()  # Query all users from the database
    return jsonify([{
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone_number": user.phone_number,
        "type": user.type
    } for user in users]), 200

@bp.route('/create-staff', methods=['POST'])
@role_required(['admin'])  # Restrict access to admin users
def create_staff_user():
    """Allow admin to create a staff user."""
    data = request.json
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone_number')
    password = data.get('password')

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already registered"}), 400

    # Create a staff user
    staff_user = User(name=name, email=email, phone_number=phone, type='staff')
    staff_user.set_password(password)
    db.session.add(staff_user)
    db.session.commit()

    return jsonify({"message": "Staff user created successfully"}), 201
