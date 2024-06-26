import os
from datetime import datetime, timedelta
import redis
from flask import current_app, redirect, url_for


def read_index_schema(pool, index_name):
    try:
        index_schema = {"tag": [], "text": [], "numeric": []}
        idx_info = redis.Redis(connection_pool=pool, decode_responses=True).ft(index_name).info()
        for field in idx_info['attributes']:
            attribute_name = field[1]
            attribute_type = field[5].lower()
            if attribute_type in index_schema:
                index_schema[attribute_type].append({"name": attribute_name})
        return index_schema
    except Exception as e:
        print(f"read_index_schema error {e}")
        return None


def history_to_json(input_string):
    json_data = []
    for conv in input_string:
        json_data.append({"type": type(conv).__name__, "content": conv.content, "context": conv.additional_kwargs})
    return json_data


def generate_redis_connection_string(url="127.0.0.1", port=6379, password=None):
    if password:
        connection_string = f"redis://:{password}@{url}:{port}"
    else:
        connection_string = f"redis://{url}:{port}"
    return connection_string


def get_db(decode_responses=False):
    try:
        return redis.Redis(connection_pool=current_app.pool, decode_responses=decode_responses)
    except redis.exceptions.ConnectionError:
        return redirect(url_for("minipilot_bp.error-page"))


def milliseconds_to_time_ago(milliseconds):
    # Convert milliseconds to seconds
    seconds = milliseconds / 1000.0

    # Get the current time
    current_time = datetime.utcnow()

    # Calculate the time ago
    time_ago = current_time - timedelta(seconds=seconds)

    # Format the time ago string
    if seconds < 60:
        return f"{int(seconds)} seconds ago"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{int(minutes)} minutes ago"
    elif seconds < 86400:
        hours = seconds / 3600
        return f"{int(hours)} hours ago"
    else:
        days = seconds / 86400
        return f"{int(days)} days ago"


def get_filename_without_extension(file_path):
    # Extract the filename from the path
    filename_with_extension = os.path.basename(file_path)
    # Remove the extension
    filename_without_extension = os.path.splitext(filename_with_extension)[0]
    return filename_without_extension