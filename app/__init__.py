"""
Flask application factory for ChurnGuard.
"""

from flask import Flask
from app.config import Config
from app.ml_model import ChurnModel
from app.data_service import DataService

# Global instances — initialized once when app starts
churn_model = None
data_service = None


def create_app():
    """Create and configure the Flask application."""
    global churn_model, data_service

    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize ML model
    churn_model = ChurnModel(Config.MODEL_PATH)

    # Initialize data service
    data_service = DataService(Config.DATA_PATH)

    # Register routes
    from app.routes import main_bp
    app.register_blueprint(main_bp)

    return app
