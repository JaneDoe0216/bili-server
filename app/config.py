import os

# Set debugging mode. False means debugging is off.
DEBUG = False

# Secret key for Flask application, fetched from environment variable or set to a default value.
SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "hanabisamasaikou")

# Host IP address for the server, "0.0.0.0" means it listens on all available network interfaces.
HOST = "0.0.0.0"

# Port number for the server to run on.
PORT = 5000

# Dictionary containing API endpoint URLs for different services.
API = {
    "generate": "https://passport.bilibili.com/x/passport-login/web/qrcode/generate",  # API to generate QR code for login
    "poll": "https://passport.bilibili.com/x/passport-login/web/qrcode/poll",  # API to poll QR code status
    "view": "https://api.bilibili.com/x/web-interface/wbi/view",  # API to get video view info
    "playurl": "https://api.bilibili.com/x/player/wbi/playurl",  # API to get video play URL
}

# Path to the directory where cache files will be stored.
CACHE_DIRECTORY = os.path.join(os.path.abspath(os.path.dirname(__file__)), "cache")

# Check if the cache directory exists; if not, create it.
if not os.path.exists(CACHE_DIRECTORY):
    os.makedirs(CACHE_DIRECTORY)
