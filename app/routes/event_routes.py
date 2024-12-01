from flask import Blueprint, request, jsonify
from app.models import Event, db
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app.utils.auth_helpers import role_required

bp = Blueprint('event_routes', __name__)

@bp.route('/create', methods=['POST'])
@jwt_required()
@role_required(['admin'])
def create_event():
    """Create a new event."""
    data = request.json
    title = data.get('title')
    description = data.get('description')
    date = data.get('date')
    time = data.get('time')
    location = data.get('location')
    image = data.get('image')  # Accept image field

    # Validate inputs
    if not all([title, description, date, time, location]):
        return jsonify({"message": "Missing required fields"}), 400

    # Convert date and time strings to datetime.date and datetime.time objects
    try:
        event_date = datetime.strptime(date, '%Y-%m-%d').date()
        event_time = datetime.strptime(time, '%H:%M:%S').time()
    except ValueError:
        return jsonify({"message": "Invalid date or time format"}), 400

    # Create and save the event
    event = Event(
        title=title,
        description=description,
        date=event_date,
        time=event_time,
        location=location,
        image=image  # Save image field
    )
    db.session.add(event)
    db.session.commit()

    return jsonify({"message": "Event created successfully"}), 201


@bp.route('/', methods=['GET'])
def list_events():
    """List all events."""
    events = Event.query.all()
    return jsonify([{
        "id": event.id,
        "title": event.title,
        "description": event.description,
        "date": str(event.date),
        "time": str(event.time),
        "location": event.location,
        "image": event.image  # Include image in response
    } for event in events]), 200



@bp.route('/<int:event_id>', methods=['GET'])
def get_event(event_id):
    """Retrieve a specific event."""
    event = Event.query.get(event_id)
    if not event:
        return jsonify({"message": "Event not found"}), 404

    return jsonify({
        "id": event.id,
        "title": event.title,
        "description": event.description,
        "date": str(event.date),
        "time": str(event.time),
        "location": event.location,
        "image": event.image  # Include image in response
    }), 200


@bp.route('/<int:event_id>', methods=['PUT'])
@jwt_required()
@role_required(['admin'])
def update_event(event_id):
    """Update an existing event."""
    event = Event.query.get(event_id)
    if not event:
        return jsonify({"message": "Event not found"}), 404

    data = request.json
    event.title = data.get('title', event.title)
    event.description = data.get('description', event.description)
    event.date = data.get('date', event.date)
    event.time = data.get('time', event.time)
    event.location = data.get('location', event.location)
    event.image = data.get('image', event.image)  # Allow image update

    db.session.commit()
    return jsonify({"message": "Event updated successfully"}), 200


@bp.route('/<int:event_id>', methods=['DELETE'])
@role_required(['admin'])
def delete_event(event_id):
    """Delete a specific event."""
    event = Event.query.get(event_id)
    if not event:
        return jsonify({"message": "Event not found"}), 404

    db.session.delete(event)
    db.session.commit()
    return jsonify({"message": "Event deleted successfully"}), 200
