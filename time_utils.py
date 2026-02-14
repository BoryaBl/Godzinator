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


def _round_half_up_non_negative(value: float) -> int:
    # Value is expected to be >= 0 in multiplier flow.
    return int(value + 0.5)


def multiply_time(time_str: str, days: int):
    seconds = time_to_seconds(time_str)
    total_seconds = seconds * days

    return (
        seconds_to_time(total_seconds),
        seconds_to_float_hours(total_seconds),
    )


def calculate_time_expression(
    times: list[str],
    operators: list[str],
    multipliers: list[float] | None = None,
):
    if not times:
        raise ValueError("times cannot be empty")

    if len(times) - 1 != len(operators):
        raise ValueError("operators length must match times length minus one")

    if multipliers is None:
        multipliers = [1.0] * len(operators)
    elif len(multipliers) != len(operators):
        raise ValueError("multipliers length must match operators length")

    total_seconds = time_to_seconds(times[0])

    for i in range(1, len(times)):
        multiplier = multipliers[i - 1]
        if multiplier < 0:
            raise ValueError("multiplier must be greater than or equal to 0")

        seconds = time_to_seconds(times[i])
        effective_seconds = _round_half_up_non_negative(seconds * multiplier)

        if operators[i - 1] == "+":
            total_seconds += effective_seconds
        elif operators[i - 1] == "-":
            total_seconds -= effective_seconds

    return (
        seconds_to_time(total_seconds),
        seconds_to_float_hours(total_seconds),
    )


def calculate_vacation_days(planned_time: str, daily_norm: str) -> float:
    planned_seconds = time_to_seconds(planned_time)
    norm_seconds = time_to_seconds(daily_norm)

    return round(planned_seconds / norm_seconds, 2)
