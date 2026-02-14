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
    def test_sanitize_digits_filters_non_digits_and_limits_to_seven_characters(self) -> None:
        self.assertEqual(sanitize_digits("ab1:2-3 4x567"), "1234567")
        self.assertEqual(sanitize_digits("987654321"), "9876543")

    def test_mask_hhmmss_progressively_formats_input(self) -> None:
        cases = {
            "": "",
            "1": "1",
            "14": "14",
            "143": "143",
            "1435": "14:35",
            "14355": "1:43:55",
            "143550": "14:35:50",
            "1435500": "143:55:00",
            "a1b4c3d5e5f0g0": "143:55:00",
        }

        for raw_value, expected in cases.items():
            with self.subTest(raw_value=raw_value):
                self.assertEqual(mask_hhmmss(raw_value), expected)

    def test_is_complete_hhmmss(self) -> None:
        self.assertFalse(is_complete_hhmmss(""))
        self.assertFalse(is_complete_hhmmss("143"))
        self.assertFalse(is_complete_hhmmss("14:35"))
        self.assertTrue(is_complete_hhmmss("1:43:55"))
        self.assertTrue(is_complete_hhmmss("12:34:56"))
        self.assertTrue(is_complete_hhmmss("143:55:00"))

    def test_format_signed_seconds(self) -> None:
        self.assertEqual(format_signed_seconds(0), "00:00:00")
        self.assertEqual(format_signed_seconds(3661), "01:01:01")
        self.assertEqual(format_signed_seconds(-3661), "-01:01:01")
        self.assertEqual(format_signed_seconds(-10), "-00:00:10")

    def test_build_expression_payload_uses_only_complete_rows(self) -> None:
        rows = [
            TimeRowState(row_id="1", operator="+", value="143:55:00"),
            TimeRowState(row_id="2", operator="-", value="14:35"),
            TimeRowState(row_id="3", operator="-", value="1:05:00"),
            TimeRowState(row_id="4", operator="+", value=""),
        ]

        times, operators, total_seconds = build_expression_payload(rows)

        self.assertEqual(times, ["00:00:00", "143:55:00", "1:05:00"])
        self.assertEqual(operators, ["+", "-"])
        self.assertEqual(total_seconds, 514200)

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
