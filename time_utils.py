def time_to_seconds(time_str: str) -> int:
    hours, minutes, seconds = map(int, time_str.split(":"))
    return hours * 3600 + minutes * 60 + seconds
