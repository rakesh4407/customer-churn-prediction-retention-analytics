"""Application configuration loaded from environment variables."""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Flask application configuration."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"

    # Paths (relative to project root)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    MODEL_PATH = os.path.join(
        BASE_DIR, os.getenv("MODEL_PATH", "model/churn_model.pkl")
    )
    DATA_PATH = os.path.join(
        BASE_DIR, os.getenv("DATA_PATH", "data/telco_churn.csv")
    )
