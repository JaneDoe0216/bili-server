import time
import random
import subprocess
from functools import wraps
from typing import Any, Callable

import requests
from flask import request, jsonify, current_app


# Decorator to validate that required parameters are present in the request query string
def validate_params(*params: str) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Check if each required parameter is in the request's query arguments
            for param in params:
                if not request.args.get(param):
                    # If a parameter is missing, return a JSON error response
                    return jsonify({"error": f"Missing parameter: {param}"})
            return func(*args, **kwargs)

        return wrapper

    return decorator


# Decorator to log information about the HTTP request
def fetch_log(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Log the method, path, and query parameters of the incoming request
        current_app.logger.info(
            f"{request.method} {request.path} - args: {request.args.to_dict()}"
        )
        return func(*args, **kwargs)

    return wrapper


# Function to get the headers required for making requests (cookie and user-agent)
def get_headers() -> dict:
    cookie = request.args.get(
        "cookie"
    )  # Retrieve the cookie parameter from the request
    user_agent = request.headers.get(
        "user-agent"
    )  # Retrieve the user-agent from the request headers
    return {
        "cookie": cookie,  # Set cookie in headers
        "referer": "https://www.bilibili.com/",  # Set referer header for requests
        "user-agent": user_agent,  # Set user-agent in headers
    }


# Function to make an HTTP GET request and return the JSON response's "data" field
def fetch(url: str, params: dict | None = None, headers: dict | None = None) -> dict:
    try:
        # Perform a GET request with the provided URL, parameters, and headers
        response = requests.get(url=url, params=params, headers=headers)
        response.raise_for_status()  # Raise an exception if the request was unsuccessful
        # Return the 'data' field from the JSON response, or an empty dict if it doesn't exist
        return response.json().get("data", {})
    except requests.exceptions.RequestException as e:
        # Log any issues with the request (e.g., network error)
        current_app.logger.error(
            f"Request failed: {e} - URL: {url} - Params: {params} - Headers: {headers}"
        )
    except Exception as e:
        # Log any other unexpected errors
        current_app.logger.error(f"Unexpected error: {e}")
    return {}


# Function to download a file from a URL and save it locally
def download_file(url: str, file: str, headers: dict | None = None) -> None:
    try:
        time.sleep(
            random.uniform(0, 1)
        )  # Sleep for a random time (to avoid rate-limiting issues)
        # Perform a GET request to download the file with the provided headers
        with requests.get(url=url, headers=headers, stream=True) as response:
            response.raise_for_status()  # Raise an exception if the request failed
            # Write the content to a local file in binary mode
            with open(file=file, mode="wb") as f:
                for chunk in response.iter_content(
                    chunk_size=1024 * 64
                ):  # Download in chunks
                    if chunk:
                        f.write(chunk)  # Write each chunk to the file
    except requests.exceptions.RequestException as e:
        # Log any issues with the request
        current_app.logger.error(
            f"Request failed: {e} - URL: {url} - File: {file} - Headers: {headers}"
        )
    except Exception as e:
        # Log any other unexpected errors
        current_app.logger.error(f"Unexpected error: {e}")


def convert_media(inputs: list[tuple[str, str]], output):
    try:
        # Initialize the FFmpeg command with common options
        commands = ["ffmpeg", "-y", "-loglevel", "error"]

        # Add input files to the command
        for input_path, input_type in inputs:
            commands += ["-i", input_path]

        # Specify the output file and codec options
        commands += ["-c", "copy", output]

        # Execute the FFmpeg command
        result = subprocess.run(commands, capture_output=True, text=True)

        # Check if the command was successful
        if result.returncode != 0:
            current_app.logger.error(f"FFmpeg failed: {result.stderr}")
    except Exception as e:
        current_app.logger.error(f"Conversion error: {e}")
