import os
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask_cors import CORS

from app.routes import bp


# Function to set up logging for the Flask app
def setup_logging(app: Flask) -> None:
    # Create a 'logs' directory if it doesn't exist
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # Set up a rotating file handler to store logs in 'logs/app.log'
    file_handler = RotatingFileHandler(
        "logs/app.log", maxBytes=1024 * 1024, backupCount=5, encoding="utf-8"
    )
    # Define the log format for the file handler
    file_handler.setFormatter(
        logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s")
    )
    file_handler.setLevel(logging.INFO)  # Set the log level to INFO for file logging

    # Set up a stream handler to log to the console (stdout)
    stream_handler = logging.StreamHandler()
    # Define the log format for the stream handler
    stream_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )

    # Set the overall log level for the app to INFO
    app.logger.setLevel(logging.INFO)
    # Add the file and stream handlers to the app's logger
    app.logger.addHandler(file_handler)
    app.logger.addHandler(stream_handler)

    # Prevent log messages from being propagated to the root logger (avoiding duplication)
    app.logger.propagate = False


# Function to create and configure the Flask app
def create_app():
    app = Flask(__name__)  # Initialize the Flask app
    app.config.from_pyfile("config.py", silent=True)  # Load configuration from a file

    setup_logging(app)  # Set up logging for the app

    app.register_blueprint(bp)  # Register the blueprint for API routes

    # Enable Cross-Origin Resource Sharing (CORS) for the /api/* routes, allowing all origins
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    return app
