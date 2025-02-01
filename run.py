from app import create_app, config

# Create the Flask application using the 'create_app' function
app = create_app()

# Run the Flask app only if this script is executed directly (not imported)
if __name__ == "__main__":
    # Start the Flask development server, using host and port from the config
    app.run(host=config.HOST, port=config.PORT)
