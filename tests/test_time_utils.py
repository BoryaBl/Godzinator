from __future__ import annotations

import unittest

from time_utils import calculate_time_expression, calculate_vacation_days


class TestTimeUtils(unittest.TestCase):
    def test_calculate_time_expression_backwards_compatible_without_multipliers(self) -> None:
        result = calculate_time_expression(
            times=["00:00:00", "01:00:00", "00:30:00"],
            operators=["+", "-"],
        )
        self.assertEqual(result, ("00:30:00", 0.5))

    def test_calculate_time_expression_with_multipliers(self) -> None:
        result = calculate_time_expression(
            times=["00:00:00", "01:00:00", "00:30:00"],
            operators=["+", "-"],
            multipliers=[1.5, 2.0],
        )
        self.assertEqual(result, ("00:30:00", 0.5))

    def test_calculate_time_expression_rounds_half_up(self) -> None:
        result = calculate_time_expression(
            times=["00:00:00", "00:00:01"],
            operators=["+"],
            multipliers=[1.5],
        )
        self.assertEqual(result, ("00:00:02", 0.0))

    def test_calculate_time_expression_raises_for_invalid_multipliers_length(self) -> None:
        with self.assertRaises(ValueError):
            calculate_time_expression(
                times=["00:00:00", "01:00:00"],
                operators=["+"],
                multipliers=[1.0, 2.0],
            )

    def test_calculate_vacation_days_with_valid_norm(self) -> None:
        self.assertEqual(calculate_vacation_days(43200, "07:35:00"), 1.58)

    def test_calculate_vacation_days_allows_negative_total_seconds(self) -> None:
        self.assertEqual(calculate_vacation_days(-21600, "08:00:00"), -0.75)

    def test_calculate_vacation_days_returns_zero_for_zero_norm(self) -> None:
        self.assertEqual(calculate_vacation_days(3600, "00:00:00"), 0.0)

    def test_calculate_vacation_days_returns_zero_for_invalid_norm(self) -> None:
        self.assertEqual(calculate_vacation_days(3600, ""), 0.0)
        self.assertEqual(calculate_vacation_days(3600, "14:35"), 0.0)


if __name__ == "__main__":
    unittest.main()
