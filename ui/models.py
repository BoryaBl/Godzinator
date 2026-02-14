from __future__ import annotations

from dataclasses import dataclass


def _only_digits(value: str) -> str:
    return "".join(character for character in value if character.isdigit())[:7]


@dataclass(slots=True)
class TimeRowState:
    row_id: str
    operator: str = "+"
    value: str = ""
    multiplier: str = "1"
    is_active: bool = True
    description: str = ""

    @property
    def digits(self) -> str:
        return _only_digits(self.value)

    @property
    def is_started(self) -> bool:
        return bool(self.digits)

    @property
    def is_complete(self) -> bool:
        return 5 <= len(self.digits) <= 7
