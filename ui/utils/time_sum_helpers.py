from __future__ import annotations

from collections.abc import Iterable

from time_utils import time_to_seconds
from ui.models import TimeRowState


def sanitize_digits(value: str) -> str:
    return "".join(character for character in value if character.isdigit())[:6]


def mask_hhmmss(value: str) -> str:
    digits = sanitize_digits(value)
    if not digits:
        return ""
    if len(digits) <= 2:
        return digits
    if len(digits) <= 4:
        return f"{digits[:2]}:{digits[2:]}"
    return f"{digits[:2]}:{digits[2:4]}:{digits[4:]}"


def is_complete_hhmmss(value: str) -> bool:
    return len(sanitize_digits(value)) == 6


def format_signed_seconds(total_seconds: int) -> str:
    sign = "-" if total_seconds < 0 else ""
    absolute_seconds = abs(total_seconds)
    hours = absolute_seconds // 3600
    minutes = (absolute_seconds % 3600) // 60
    seconds = absolute_seconds % 60
    return f"{sign}{hours:02}:{minutes:02}:{seconds:02}"


def digits_to_hhmmss(value: str) -> str:
    digits = sanitize_digits(value)
    if len(digits) != 6:
        raise ValueError("Time value must contain exactly 6 digits")
    return f"{digits[:2]}:{digits[2:4]}:{digits[4:6]}"


def build_expression_payload(rows: Iterable[TimeRowState]) -> tuple[list[str], list[str], int]:
    times = ["00:00:00"]
    operators: list[str] = []
    total_seconds = 0

    for row in rows:
        if not row.is_complete:
            continue

        operator = row.operator if row.operator in {"+", "-"} else "+"
        time_value = digits_to_hhmmss(row.digits)

        times.append(time_value)
        operators.append(operator)

        row_seconds = time_to_seconds(time_value)
        total_seconds += row_seconds if operator == "+" else -row_seconds

    return times, operators, total_seconds
