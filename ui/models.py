from __future__ import annotations

from dataclasses import dataclass


def _only_digits(value: str) -> str:
    return "".join(character for character in value if character.isdigit())[:6]


@dataclass(slots=True)
class TimeRowState:
    row_id: str
    operator: str = "+"
    value: str = ""

    @property
    def digits(self) -> str:
        return _only_digits(self.value)

    @property
    def is_started(self) -> bool:
        return bool(self.digits)

    @property
    def is_complete(self) -> bool:
        return len(self.digits) == 6
