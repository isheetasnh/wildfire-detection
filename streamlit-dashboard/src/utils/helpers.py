# load JSON data from a local file
def load_json_data(file_path):
    import json
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

# format a timestamp object into a human readable string
def format_timestamp(timestamp):
    from datetime import datetime
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')