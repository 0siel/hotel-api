from flask import Blueprint, request, jsonify
from app.models import Room, db
from app.utils.auth_helpers import role_required

bp = Blueprint('room_routes', __name__)

@bp.before_request
def log_request_info():
    print(f"Headers: {request.headers}")
    print(f"Body: {request.get_data()}")


@bp.route('/create', methods=['POST'])
@role_required(['admin'])
def create_room():
    """Create a new room."""
    """Create a new room."""
    try:
        print(f"Raw Data: {request.data}")  # Log raw request body
        data = request.json
        print(f"Parsed JSON: {data}")  # Debug log
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        return jsonify({"message": "Invalid JSON format"}), 400
    
    """Create a new room."""
    data = request.json
    name = data.get('name')
    description = data.get('description')
    square_meters = data.get('square_meters')
    price_per_night = data.get('price_per_night')
    images_list = data.get('images_list', [])

    if not all([name, description, square_meters, price_per_night]):
        return jsonify({"message": "Missing required fields"}), 400

    room = Room(
        name=name,
        description=description,
        square_meters=square_meters,
        price_per_night=price_per_night,
        images_list=images_list
    )
    db.session.add(room)
    db.session.commit()

    return jsonify({"message": "Room created successfully"}), 201


@bp.route('/', methods=['GET'])
def list_rooms():
    """List all rooms."""
    rooms = Room.query.all()
    return jsonify([{
        "id": room.id,
        "name": room.name,
        "description": room.description,
        "square_meters": room.square_meters,
        "price_per_night": room.price_per_night,
        "images_list": room.images_list
    } for room in rooms]), 200


@bp.route('/<int:room_id>', methods=['GET'])
def get_room(room_id):
    """Retrieve details of a specific room."""
    room = Room.query.get(room_id)
    if not room:
        return jsonify({"message": "Room not found"}), 404

    return jsonify({
        "id": room.id,
        "name": room.name,
        "description": room.description,
        "square_meters": room.square_meters,
        "price_per_night": room.price_per_night,
        "images_list": room.images_list
    }), 200


@bp.route('/<int:room_id>', methods=['PUT'])
@role_required(['admin'])
def update_room(room_id):
    """Update details of a specific room."""
    room = Room.query.get(room_id)
    if not room:
        return jsonify({"message": "Room not found"}), 404

    data = request.json
    room.name = data.get('name', room.name)
    room.description = data.get('description', room.description)
    room.square_meters = data.get('square_meters', room.square_meters)
    room.price_per_night = data.get('price_per_night', room.price_per_night)
    room.images_list = data.get('images_list', room.images_list)

    db.session.commit()
    return jsonify({"message": "Room updated successfully"}), 200


@bp.route('/<int:room_id>', methods=['DELETE'])
@role_required(['admin'])
def delete_room(room_id):
    """Delete a specific room."""
    room = Room.query.get(room_id)
    if not room:
        return jsonify({"message": "Room not found"}), 404

    db.session.delete(room)
    db.session.commit()
    return jsonify({"message": "Room deleted successfully"}), 200