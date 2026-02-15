from __future__ import annotations

from ui.utils.time_sum_helpers import is_complete_hhmmss
from time_utils import time_to_seconds


def sanitize_decimal_input(raw: str) -> tuple[str, bool]:
    result: list[str] = []
    separator_added = False
    had_invalid = False

    for character in raw:
        if character.isdigit():
            result.append(character)
            continue

        if character in {".", ","}:
            if separator_added:
                had_invalid = True
                continue

            result.append(character)
            separator_added = True
            continue

        had_invalid = True

    return "".join(result), had_invalid


def normalize_decimal(raw: str) -> str:
    return raw.strip().replace(",", ".")


def parse_non_negative_float(raw: str) -> float | None:
    normalized = normalize_decimal(raw)
    if not normalized:
        return None

    if normalized.count(".") > 1:
        return None

    if any(character not in "0123456789." for character in normalized):
        return None

    if normalized == ".":
        return None

    try:
        value = float(normalized)
    except ValueError:
        return None

    if value < 0:
        return None

    return value


def round_half_up_non_negative(value: float) -> int:
    return int(value + 0.5)


def format_float_compact(value: float) -> str:
    rounded = round(value, 4)
    if rounded.is_integer():
        return str(int(rounded))
    return f"{rounded:.4f}".rstrip("0").rstrip(".")


def is_complete_clock(value: str) -> bool:
    return is_complete_hhmmss(value)


def parse_complete_clock_to_seconds(value: str) -> int | None:
    if not is_complete_clock(value):
        return None

    parts = value.split(":")
    if len(parts) != 3:
        return None

    try:
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = int(parts[2])
    except ValueError:
        return None

    if hours < 0 or minutes < 0 or seconds < 0:
        return None

    if minutes > 59 or seconds > 59:
        return None

    try:
        return time_to_seconds(value)
    except ValueError:
        return None
