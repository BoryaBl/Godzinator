from __future__ import annotations

import unittest

from ui.models import TimeRowState
from ui.utils.time_sum_helpers import (
    build_expression_payload,
    format_signed_seconds,
    is_complete_hhmmss,
    mask_hhmmss,
    sanitize_digits,
)


class TestTimeSumHelpers(unittest.TestCase):
    def test_sanitize_digits_filters_non_digits_and_limits_to_six_characters(self) -> None:
        self.assertEqual(sanitize_digits("ab1:2-3 4x56"), "123456")
        self.assertEqual(sanitize_digits("987654321"), "987654")

    def test_mask_hhmmss_progressively_formats_input(self) -> None:
        cases = {
            "": "",
            "1": "1",
            "12": "12",
            "123": "12:3",
            "1234": "12:34",
            "12345": "12:34:5",
            "123456": "12:34:56",
            "12:34:56": "12:34:56",
            "a1b2c3d4e5f6": "12:34:56",
        }

        for raw_value, expected in cases.items():
            with self.subTest(raw_value=raw_value):
                self.assertEqual(mask_hhmmss(raw_value), expected)

    def test_is_complete_hhmmss(self) -> None:
        self.assertFalse(is_complete_hhmmss(""))
        self.assertFalse(is_complete_hhmmss("12:34"))
        self.assertFalse(is_complete_hhmmss("12345"))
        self.assertTrue(is_complete_hhmmss("12:34:56"))

    def test_format_signed_seconds(self) -> None:
        self.assertEqual(format_signed_seconds(0), "00:00:00")
        self.assertEqual(format_signed_seconds(3661), "01:01:01")
        self.assertEqual(format_signed_seconds(-3661), "-01:01:01")
        self.assertEqual(format_signed_seconds(-10), "-00:00:10")

    def test_build_expression_payload_uses_only_complete_rows(self) -> None:
        rows = [
            TimeRowState(row_id="1", operator="+", value="01:00:00"),
            TimeRowState(row_id="2", operator="-", value="020"),
            TimeRowState(row_id="3", operator="-", value="00:30:00"),
            TimeRowState(row_id="4", operator="+", value=""),
        ]

        times, operators, total_seconds = build_expression_payload(rows)

        self.assertEqual(times, ["00:00:00", "01:00:00", "00:30:00"])
        self.assertEqual(operators, ["+", "-"])
        self.assertEqual(total_seconds, 1800)

    def test_build_expression_payload_falls_back_to_plus_for_invalid_operator(self) -> None:
        rows = [
            TimeRowState(row_id="1", operator="*", value="00:15:00"),
        ]

        times, operators, total_seconds = build_expression_payload(rows)

        self.assertEqual(times, ["00:00:00", "00:15:00"])
        self.assertEqual(operators, ["+"])
        self.assertEqual(total_seconds, 900)


if __name__ == "__main__":
    unittest.main()
