from datetime import datetime


def convert_timestamp_to_seconds(
    timestamp_format: str, timestamp_str: str
) -> int | None:
    try:
        timestamp = datetime.strptime(timestamp_str, timestamp_format)
        timestamp_seconds = int(timestamp.timestamp())
        return timestamp_seconds

    except ValueError as e:
        print(f"Error parsing timestamp: {e}")
        return None


def format_time_difference(seconds: int) -> str:
    minutes = seconds // 60
    hours = minutes // 60
    days = hours // 24

    if days > 0:
        return f"{days} day{'s' if days > 1 else ''} ago"
    elif hours > 0:
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif minutes > 0:
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return f"{seconds} second{'s' if seconds > 1 else ''} ago"
