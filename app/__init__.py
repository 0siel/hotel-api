from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from config import Config
from flask_cors import CORS

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Enable CORS for all domains on all routes (for testing)
    CORS(app)

    # Register Blueprints
    from app.routes import user_routes, room_routes, task_routes, reservation_routes, event_routes
    app.register_blueprint(user_routes, url_prefix='/api/users', name='users_routes')
    app.register_blueprint(room_routes, url_prefix='/api/rooms')
    app.register_blueprint(task_routes, url_prefix='/api/tasks')
    app.register_blueprint(reservation_routes, url_prefix='/api/reservations')
    app.register_blueprint(event_routes, url_prefix='/api/events')

    return app
