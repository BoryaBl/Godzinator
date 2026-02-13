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

def calculate_time_expression(times: list[str], operators: list[str]):
    total_seconds = time_to_seconds(times[0])

    for i in range(1, len(times)):
        seconds = time_to_seconds(times[i])
        if operators[i - 1] == "+":
            total_seconds += seconds
        elif operators[i - 1] == "-":
            total_seconds -= seconds

    return (
        seconds_to_time(total_seconds),
        seconds_to_float_hours(total_seconds)
    )

def calculate_vacation_days(planned_time: str, daily_norm: str) -> float:
    planned_seconds = time_to_seconds(planned_time)
    norm_seconds = time_to_seconds(daily_norm)

    return round(planned_seconds / norm_seconds, 2)


