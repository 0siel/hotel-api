from flask import Blueprint, request, jsonify
from app.models import Task, User, db
from datetime import datetime
from app.utils.auth_helpers import role_required

bp = Blueprint('task_routes', __name__)

bp = Blueprint('task_routes', __name__)

@bp.route('/create', methods=['POST'])
@role_required(['admin'])
def create_task():
    """Create a new task."""
    data = request.json
    title = data.get('title')
    description = data.get('description')
    due_date = data.get('due_date')
    status = data.get('status', 'pending')  # Default status is 'pending'
    user_assigned = data.get('user_assigned')

    # Validate required fields
    if not all([title, description, due_date]):
        return jsonify({"message": "Missing required fields"}), 400

    # Convert due_date string to datetime.datetime object
    try:
        due_date_obj = datetime.strptime(due_date, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return jsonify({"message": "Invalid due_date format. Use YYYY-MM-DD HH:MM:SS"}), 400

    # Check if the assigned user exists (optional validation)
    if user_assigned and not db.session.query(User.id).filter_by(id=user_assigned).first():
        return jsonify({"message": "Assigned user not found"}), 404

    # Create and save the task
    task = Task(
        title=title,
        description=description,
        due_date=due_date_obj,
        status=status,
        user_assigned=user_assigned
    )
    db.session.add(task)
    db.session.commit()

    return jsonify({"message": "Task created successfully"}), 201

@bp.route('/', methods=['GET'])
@role_required(['admin, staff'])
def list_tasks():
    """List all tasks."""
    tasks = Task.query.all()
    return jsonify([{
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "due_date": task.due_date,
        "status": task.status,
        "user_assigned": task.user_assigned
    } for task in tasks]), 200


@bp.route('/<int:task_id>', methods=['GET'])
@role_required(['admin', 'staff'])
def get_task(task_id):
    """Retrieve a specific task."""
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"message": "Task not found"}), 404

    return jsonify({
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "due_date": task.due_date,
        "status": task.status,
        "user_assigned": task.user_assigned
    }), 200


@bp.route('/<int:task_id>', methods=['PUT'])
@role_required(['admin', 'staff'])
def update_task(task_id):
    """Update an existing task."""
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"message": "Task not found"}), 404

    data = request.json
    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.due_date = data.get('due_date', task.due_date)
    task.status = data.get('status', task.status)
    task.user_assigned = data.get('user_assigned', task.user_assigned)

    db.session.commit()
    return jsonify({"message": "Task updated successfully"}), 200


@bp.route('/<int:task_id>', methods=['DELETE'])
@role_required(['admin'])
def delete_task(task_id):
    """Delete a specific task."""
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"message": "Task not found"}), 404

    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted successfully"}), 200
