from __future__ import annotations

from collections.abc import Iterable

from time_utils import time_to_seconds
from ui.models import TimeRowState


def sanitize_digits(value: str) -> str:
    return "".join(character for character in value if character.isdigit())[:7]


def mask_hhmmss(value: str) -> str:
    digits = sanitize_digits(value)
    length = len(digits)

    if length <= 3:
        return digits
    if length == 4:
        return f"{digits[:2]}:{digits[2:]}"
    return f"{digits[:-4]}:{digits[-4:-2]}:{digits[-2:]}"


def is_complete_hhmmss(value: str) -> bool:
    return 5 <= len(sanitize_digits(value)) <= 7


def sanitize_multiplier_text(raw: str) -> str:
    result: list[str] = []
    separator_added = False

    for character in raw:
        if character.isdigit():
            result.append(character)
        elif character in ".," and not separator_added:
            result.append(character)
            separator_added = True

    return "".join(result)


def normalize_multiplier(raw: str) -> str:
    return raw.strip().replace(",", ".")


def parse_multiplier(raw: str) -> float | None:
    normalized = normalize_multiplier(raw)
    if not normalized:
        return None

    if normalized.count(".") > 1:
        return None

    if any(character not in "0123456789." for character in normalized):
        return None

    if normalized in {".", "+", "-", "+.", "-."}:
        return None

    try:
        value = float(normalized)
    except ValueError:
        return None

    if value < 0:
        return None

    return value


def is_valid_multiplier(raw: str) -> bool:
    return parse_multiplier(raw) is not None


def format_signed_seconds(total_seconds: int) -> str:
    sign = "-" if total_seconds < 0 else ""
    absolute_seconds = abs(total_seconds)
    hours = absolute_seconds // 3600
    minutes = (absolute_seconds % 3600) // 60
    seconds = absolute_seconds % 60
    return f"{sign}{hours:02}:{minutes:02}:{seconds:02}"


def digits_to_hhmmss(value: str) -> str:
    digits = sanitize_digits(value)
    if not 5 <= len(digits) <= 7:
        raise ValueError("Time value must contain from 5 to 7 digits")
    return f"{digits[:-4]}:{digits[-4:-2]}:{digits[-2:]}"


def round_half_up_non_negative(value: float) -> int:
    return int(value + 0.5)


def build_expression_payload(rows: Iterable[TimeRowState]) -> tuple[list[str], list[str], list[float], int]:
    times = ["00:00:00"]
    operators: list[str] = []
    multipliers: list[float] = []
    total_seconds = 0

    for row in rows:
        if not row.is_active:
            continue

        if not row.is_complete:
            continue

        multiplier = parse_multiplier(row.multiplier)
        if multiplier is None:
            continue

        operator = row.operator if row.operator in {"+", "-"} else "+"
        time_value = digits_to_hhmmss(row.digits)

        times.append(time_value)
        operators.append(operator)
        multipliers.append(multiplier)

        row_seconds = time_to_seconds(time_value)
        effective_seconds = round_half_up_non_negative(row_seconds * multiplier)
        total_seconds += effective_seconds if operator == "+" else -effective_seconds

    return times, operators, multipliers, total_seconds
