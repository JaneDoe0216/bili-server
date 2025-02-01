import os
from urllib.parse import urlparse

from flask import Blueprint, jsonify, send_file, request

from app import config
from app.utils import (
    validate_params,
    fetch,
    fetch_log,
    get_headers,
    download_file,
    convert_media,
)

# Create a Blueprint for API routes with a URL prefix of "/api"
bp = Blueprint("api", __name__, url_prefix="/api")


# Route to generate a QR code for login (using the 'generate' API)
@bp.get("/generate")
@fetch_log  # Log the request details
def generate():
    # Fetch data from the 'generate' API and return it as JSON
    data = fetch(url=config.API.get("generate"), headers=get_headers())
    return jsonify(data)


# Route to poll the status of the QR code (using the 'poll' API)
@bp.get("/poll")
@fetch_log  # Log the request details
@validate_params("qrcode_key")  # Ensure 'qrcode_key' is present in the request
def poll():
    qrcode_key = request.args.get(
        "qrcode_key"
    )  # Retrieve the 'qrcode_key' parameter from the request
    params = {
        "qrcode_key": qrcode_key
    }  # Set the 'qrcode_key' in the API request parameters
    # Fetch data from the 'poll' API and return it as JSON
    data = fetch(url=config.API.get("poll"), params=params, headers=get_headers())
    return jsonify(data)


# Route to fetch video view information (using the 'view' API)
@bp.get("/view")
@fetch_log  # Log the request details
@validate_params(
    "bvid", "cookie"
)  # Ensure 'bvid' and 'cookie' are present in the request
def view():
    bvid = request.args.get("bvid")  # Retrieve the 'bvid' parameter from the request
    params = {"bvid": bvid}  # Set the 'bvid' in the API request parameters
    # Fetch data from the 'view' API and return it as JSON
    data = fetch(url=config.API.get("view"), params=params, headers=get_headers())
    return jsonify(data)


# Route to fetch the video play URL (using the 'playurl' API)
@bp.get("/playurl")
@fetch_log  # Log the request details
@validate_params(
    "bvid", "cid", "cookie"
)  # Ensure 'bvid', 'cid', and 'cookie' are present in the request
def playurl():
    bvid = request.args.get("bvid")  # Retrieve the 'bvid' parameter from the request
    cid = request.args.get("cid")  # Retrieve the 'cid' parameter from the request
    # Set the parameters required by the 'playurl' API
    params = {
        "bvid": bvid,
        "cid": cid,
        "qn": 127,  # Quality number (for video resolution)
        "fnval": 4048,  # Function value (specific to the video player)
        "fnver": 0,  # Function version
        "fourk": 1,  # Enable 4K if available
    }
    # Fetch data from the 'playurl' API and return it as JSON
    data = fetch(url=config.API.get("playurl"), params=params, headers=get_headers())
    return jsonify(data)


@bp.get("/audio")
@validate_params(
    "aurl", "filename", "cookie"
)  # Ensure required parameters are provided
def audio():
    audio_url = request.args.get("aurl")  # Get the audio URL from the request
    filename = request.args.get("filename")  # Get the desired output filename
    cache = config.CACHE_DIRECTORY  # Cache directory path
    # Generate the local path for the audio file to be downloaded
    audio_m4s = os.path.join(cache, os.path.basename(urlparse(audio_url).path))
    # Define the output path for the converted audio file (FLAC format)
    output_path = os.path.join(cache, f"{filename}.flac")

    # If the converted file already exists, send it as an attachment
    if os.path.exists(output_path):
        return send_file(output_path, as_attachment=True)

    # Download the audio file to the local cache
    download_file(url=audio_url, file=audio_m4s, headers=get_headers())

    # Convert the downloaded audio file to the desired format (FLAC)
    convert_media([(audio_m4s, "audio")], output_path)

    # Return the converted audio file as an attachment
    return send_file(output_path, as_attachment=True)


@bp.get("/video")
@validate_params(
    "aurl", "vurl", "filename", "cookie"
)  # Ensure required parameters are provided
def video():
    audio_url = request.args.get("aurl")  # Get the audio URL from the request
    video_url = request.args.get("vurl")  # Get the video URL from the request
    filename = request.args.get("filename")  # Get the desired output filename
    cache = config.CACHE_DIRECTORY  # Cache directory path
    # Generate the local path for the audio file to be downloaded
    audio_m4s = os.path.join(cache, os.path.basename(urlparse(audio_url).path))
    # Generate the local path for the video file to be downloaded
    video_m4s = os.path.join(cache, os.path.basename(urlparse(video_url).path))
    # Define the output path for the combined video file (MKV format)
    output_path = os.path.join(cache, f"{filename}.mkv")

    # If the converted file already exists, send it as an attachment
    if os.path.exists(output_path):
        return send_file(output_path, as_attachment=True)

    # Download the audio file to the local cache
    download_file(url=audio_url, file=audio_m4s, headers=get_headers())
    # Download the video file to the local cache
    download_file(url=video_url, file=video_m4s, headers=get_headers())

    # Convert both the audio and video files and combine them into a single file (MKV)
    convert_media([(audio_m4s, "audio"), (video_m4s, "video")], output_path)

    # Return the combined video file as an attachment
    return send_file(output_path, as_attachment=True)
