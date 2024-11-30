from flask import Blueprint, request, jsonify
from app.models import Reservation, Room, User, db
from datetime import datetime
from flask_jwt_extended import get_jwt_identity
from app.utils.auth_helpers import role_required

bp = Blueprint('reservation_routes', __name__)

@bp.route('/create', methods=['POST'])
def create_reservation():
    """Create a new reservation."""
    data = request.json
    room_id = data.get('room_id')
    customer_id = data.get('customer_id')
    nights = data.get('nights')
    check_in = data.get('check_in')
    check_out = data.get('check_out')
    price = data.get('price')

    # Validate inputs
    if not all([room_id, customer_id, nights, check_in, check_out, price]):
        return jsonify({"message": "Missing required fields"}), 400

    # Convert check_in and check_out to datetime.date objects
    try:
        check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
        check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"message": "Invalid date format. Use YYYY-MM-DD"}), 400

    # Check if the room exists
    room = Room.query.get(room_id)
    if not room:
        return jsonify({"message": "Room not found"}), 404

    # Check if the customer exists
    customer = User.query.get(customer_id)
    if not customer:
        return jsonify({"message": "Customer not found"}), 404

    # Create and save the reservation
    reservation = Reservation(
        room_id=room_id,
        customer_id=customer_id,
        nights=nights,
        check_in=check_in_date,
        check_out=check_out_date,
        price=price
    )
    db.session.add(reservation)
    db.session.commit()

    return jsonify({"message": "Reservation created successfully"}), 201

@bp.route('/', methods=['GET'])
def list_reservations():
    """List all reservations."""
    reservations = Reservation.query.all()
    return jsonify([{
        "id": reservation.id,
        "room_id": reservation.room_id,
        "customer_id": reservation.customer_id,
        "nights": reservation.nights,
        "check_in": reservation.check_in,
        "check_out": reservation.check_out,
        "price": reservation.price
    } for reservation in reservations]), 200


@bp.route('/<int:reservation_id>', methods=['GET'])
@role_required(['admin'])
def get_reservation(reservation_id):
    """Retrieve a specific reservation."""
    reservation = Reservation.query.get(reservation_id)
    if not reservation:
        return jsonify({"message": "Reservation not found"}), 404

    return jsonify({
        "id": reservation.id,
        "room_id": reservation.room_id,
        "customer_id": reservation.customer_id,
        "nights": reservation.nights,
        "check_in": reservation.check_in,
        "check_out": reservation.check_out,
        "price": reservation.price
    }), 200


@bp.route('/<int:reservation_id>', methods=['PUT'])
@role_required(['admin'])
def update_reservation(reservation_id):
    """Update an existing reservation."""
    reservation = Reservation.query.get(reservation_id)
    if not reservation:
        return jsonify({"message": "Reservation not found"}), 404

    data = request.json
    reservation.nights = data.get('nights', reservation.nights)
    reservation.check_in = data.get('check_in', reservation.check_in)
    reservation.check_out = data.get('check_out', reservation.check_out)
    reservation.price = data.get('price', reservation.price)

    db.session.commit()
    return jsonify({"message": "Reservation updated successfully"}), 200


@bp.route('/<int:reservation_id>', methods=['DELETE'])
@role_required(['admin'])
def delete_reservation(reservation_id):
    """Delete a specific reservation."""
    reservation = Reservation.query.get(reservation_id)
    if not reservation:
        return jsonify({"message": "Reservation not found"}), 404

    db.session.delete(reservation)
    db.session.commit()
    return jsonify({"message": "Reservation deleted successfully"}), 200

@bp.route('/my-reservations', methods=['GET'])
@role_required(['customer'])  # Restrict access to customers only
def my_reservations():
    """Retrieve reservations for the logged-in customer."""
    user = get_jwt_identity()  # Extract customer identity from JWT
    reservations = Reservation.query.filter_by(customer_id=user['id']).all()
    
    # Return a list of reservations for the logged-in customer
    return jsonify([
        {
            "id": res.id,
            "room_id": res.room_id,
            "check_in": res.check_in.strftime('%Y-%m-%d'),  # Format datetime for JSON response
            "check_out": res.check_out.strftime('%Y-%m-%d'),
            "price": res.price
        }
        for res in reservations
    ]), 200
