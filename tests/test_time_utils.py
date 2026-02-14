from __future__ import annotations

import unittest

from time_utils import calculate_time_expression


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


if __name__ == "__main__":
    unittest.main()
