from flask import Blueprint, request, jsonify
from app.models import Event, db
from datetime import datetime
from app.utils.auth_helpers import role_required

bp = Blueprint('event_routes', __name__)

@bp.route('/create', methods=['POST'])
@role_required(['admin'])
def create_event():
    """Create a new event."""
    data = request.json
    title = data.get('title')
    description = data.get('description')
    date = data.get('date')
    time = data.get('time')
    location = data.get('location')

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
        location=location
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
        "date": event.date,
        "time": event.time,
        "location": event.location
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
        "date": event.date,
        "time": event.time,
        "location": event.location
    }), 200


@bp.route('/<int:event_id>', methods=['PUT'])
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
