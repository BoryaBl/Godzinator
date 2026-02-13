def time_to_seconds(time_str: str) -> int:
    hours, minutes, seconds = map(int, time_str.split(":"))
    return hours * 3600 + minutes * 60 + seconds

def seconds_to_time(seconds: int) -> str:
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02}:{minutes:02}:{secs:02}"

def seconds_to_float_hours(seconds: int) -> float:
    return round(seconds / 3600, 2)

def multiply_time(time_str: str, days: int):
    seconds = time_to_seconds(time_str)
    total_seconds = seconds * days

    return (
        seconds_to_time(total_seconds),
        seconds_to_float_hours(total_seconds)
    )

