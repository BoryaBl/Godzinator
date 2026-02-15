from __future__ import annotations

import unittest

from ui.utils.time_converter_helpers import (
    format_float_compact,
    parse_complete_clock_to_seconds,
    parse_non_negative_float,
    round_half_up_non_negative,
    sanitize_decimal_input,
)


class TestTimeConverterHelpers(unittest.TestCase):
    def test_sanitize_decimal_input_filters_invalid_characters(self) -> None:
        value, had_invalid = sanitize_decimal_input("ab1,5x")
        self.assertEqual(value, "1,5")
        self.assertTrue(had_invalid)

        value, had_invalid = sanitize_decimal_input("12.34")
        self.assertEqual(value, "12.34")
        self.assertFalse(had_invalid)

    def test_parse_non_negative_float(self) -> None:
        self.assertEqual(parse_non_negative_float("1"), 1.0)
        self.assertEqual(parse_non_negative_float("1.5"), 1.5)
        self.assertEqual(parse_non_negative_float("1,5"), 1.5)
        self.assertEqual(parse_non_negative_float("0"), 0.0)

        self.assertIsNone(parse_non_negative_float(""))
        self.assertIsNone(parse_non_negative_float("-1"))
        self.assertIsNone(parse_non_negative_float("1..2"))
        self.assertIsNone(parse_non_negative_float("abc"))

    def test_round_half_up_non_negative(self) -> None:
        self.assertEqual(round_half_up_non_negative(1.5), 2)
        self.assertEqual(round_half_up_non_negative(1.49), 1)

    def test_format_float_compact(self) -> None:
        self.assertEqual(format_float_compact(90.0), "90")
        self.assertEqual(format_float_compact(1.5), "1.5")
        self.assertEqual(format_float_compact(0.016666), "0.0167")

    def test_parse_complete_clock_to_seconds(self) -> None:
        self.assertEqual(parse_complete_clock_to_seconds("07:35:00"), 27300)
        self.assertEqual(parse_complete_clock_to_seconds("1:43:55"), 6235)

        self.assertIsNone(parse_complete_clock_to_seconds("0:73:50"))
        self.assertIsNone(parse_complete_clock_to_seconds("14:3"))
        self.assertIsNone(parse_complete_clock_to_seconds(""))


if __name__ == "__main__":
    unittest.main()
