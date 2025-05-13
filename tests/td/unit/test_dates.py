import unittest
from datetime import datetime
import pytz
from freezegun import freeze_time  # You'll need to add this dependency

from td.utils.dates import DT


@freeze_time("2025-05-13 12:00:00")
class TestDT(unittest.TestCase):
    """Test the DT (DateTime) utility class."""

    def test_debug_format_parsing(self):
        """Test parsing of debug format strings."""
        test_cases = [
            # (input, expected_output, description)
            ("202505141900", "202505141900", "Full YYYYMMDDHHMM format"),
            ("20250513", "202505130000", "YYYYMMDD format (assumes 00:00)"),
            ("1730", "202505131730", "HHMM format (assumes today)"),
            ("17", "202505131700", "HH format (assumes today at :00)"),
        ]

        for input_str, expected_output, description in test_cases:
            with self.subTest(
                input=input_str, expected=expected_output, desc=description
            ):
                dt = DT(input_str)
                self.assertEqual(dt.as_debug(), expected_output)

    def test_natural_format_parsing(self):
        """Test parsing of natural language date expressions."""
        test_cases = [
            # (input, expected_output, description)
            ("tonight", "202505132200", "tonight maps to 10 PM today"),
            ("this evening", "202505131830", "this evening maps to 6:30 PM today"),
            (
                "tomorrow morning",
                "202505140800",
                "tomorrow morning maps to 8 AM tomorrow",
            ),
        ]

        for input_str, expected_output, description in test_cases:
            with self.subTest(
                input=input_str, expected=expected_output, desc=description
            ):
                self.assertEqual(DT(input_str).as_debug(), expected_output)

    def test_as_strict(self):
        """Test conversion to strict format."""
        test_cases = [
            # (input, expected_obj, format, verification)
            # For object format
            ("202505131730", datetime(2025, 5, 13, 17, 30), "object", None),
            # For ISO format
            ("202505131730", None, "iso", "2025-05-13T17:30:00+"),
        ]

        for input_str, expected_obj, format_type, verification in test_cases:
            with self.subTest(input=input_str, format=format_type):
                dt = DT(input_str)
                if format_type == "object":
                    self.assertEqual(dt.as_strict(), expected_obj)
                else:
                    iso_string = dt.as_strict(format=format_type)
                    self.assertTrue(iso_string.startswith(verification))

    def test_invalid_input(self):
        """Test handling of invalid input."""
        invalid_cases = [
            ("tomorrow yesterday", "Contradictory date terms"),
            ("Feb 30", "Invalid date"),
            ("202513131200", "Invalid month"),
            ("202505321200", "Invalid day"),
            ("202505132500", "Invalid hour"),
            ("202505131260", "Invalid minute"),
            ("garbage text", "Non-date text"),
        ]

        for input_str, description in invalid_cases:
            with self.subTest(input=input_str, desc=description):
                with self.assertRaises(ValueError):
                    DT(input_str)

    def test_natural_expressions(self):
        """Test conversion to natural expressions."""
        test_cases = [
            ("202505130800", "morning"),
            ("202505131059", "morning"),
            ("202505131100", "late morning"),
            ("202505131200", "noon"),
            ("202505131230", "early afternoon"),
            ("202505131400", "afternoon"),
            ("202505131700", "early evening"),
            ("202505131830", "evening"),
            ("202505132100", "late evening"),
            ("202505132200", "tonight"),
            ("202505132330", "late night"),
            ("202505140100", "early morning (next day)"),
        ]
        for dt_str, expected_natural in test_cases:
            with self.subTest(dt_str=dt_str, expected_natural=expected_natural):
                self.assertEqual(
                    DT(dt_str).n,
                    expected_natural,
                    f"Failed for {dt_str} != {expected_natural}",
                )

    def test_natural_verbose_expressions(self):
        """Test conversion to verbose natural expressions."""
        # Today/Current time expressions
        today_cases = [
            ("202505130800", "morning, 8am"),
            ("202505131059", "morning, 10:59am"),
            ("202505131100", "late morning, 11am"),
            ("202505131200", "noon, 12pm"),
        ]

        for dt_str, expected_verbose in today_cases:
            with self.subTest(
                dt_str=dt_str, expected=expected_verbose, category="today"
            ):
                self.assertEqual(DT(dt_str).nv, expected_verbose)

        # Future expressions
        future_cases = [
            ("202505140800", "tomorrow morning, 8am"),
            ("202505150800", "day after tomorrow, 8am"),
            # ("202505161000", "this Thursday, 10am"),
            # ("202505171000", "this Friday, 10am"),
            # ("202505231000", "next Thursday, 10am"),
            # ("202506041000", "in 3 weeks, Tuesday 10am"),
            # ("202506131000", "next month, 13th at 10am"),
            # ("202507131000", "in 2 months, 13th at 10am"),
            # ("202605131000", "next year, 13th May at 10am"),
        ]

        for dt_str, expected_verbose in future_cases:
            with self.subTest(
                dt_str=dt_str, expected=expected_verbose, category="future"
            ):
                self.assertEqual(DT(dt_str).nv, expected_verbose)

        # Past expressions
        past_cases = [
            # ("202505120800", "yesterday morning, 8am"),
            ("202505110800", "day before yesterday, 8am"),
            # ("202505091000", "last Thursday, 10am"),
            ("202504131000", "last month, 13th at 10am"),
            ("202503131000", "2 months ago, 13th at 10am"),
            ("202405131000", "last year, 13th May at 10am"),
        ]

        for dt_str, expected_verbose in past_cases:
            with self.subTest(
                dt_str=dt_str, expected=expected_verbose, category="past"
            ):
                self.assertEqual(DT(dt_str).nv, expected_verbose)

    def test_shift_method(self):
        """Test shifting a datetime."""
        dt = DT("202505131200")  # noon today

        shift_cases = [
            # (days, hours, minutes, expected_result, description)
            (1, 2, 30, "202505141430", "Shift forward to tomorrow at 2:30 PM"),
            (-1, -2, -30, "202505120930", "Shift backward to yesterday at 9:30 AM"),
            (0, 5, 0, "202505131700", "Shift forward by hours only"),
            (0, 0, 45, "202505131245", "Shift forward by minutes only"),
            (7, 0, 0, "202505201200", "Shift forward by a week"),
        ]

        for days, hours, minutes, expected, description in shift_cases:
            with self.subTest(
                days=days,
                hours=hours,
                minutes=minutes,
                expected=expected,
                desc=description,
            ):
                shifted = dt.shift(days=days, hours=hours, minutes=minutes)
                self.assertEqual(shifted.as_debug(), expected)

    def test_with_time_method(self):
        """Test changing the time of a datetime."""
        dt = DT("20250513")  # today at midnight

        time_cases = [
            # (time_str, expected_result, description)
            ("10:30am", "202505131030", "12-hour format with minutes (AM)"),
            ("2:45pm", "202505131445", "12-hour format with minutes (PM)"),
            ("22:15", "202505132215", "24-hour format with minutes"),
            ("14", "202505131400", "Hour-only format (24-hour)"),
            ("8am", "202505130800", "12-hour format without minutes (AM)"),
            ("9pm", "202505132100", "12-hour format without minutes (PM)"),
            ("12am", "202505130000", "12-hour midnight format"),
            ("12pm", "202505131200", "12-hour noon format"),
        ]

        for time_str, expected, description in time_cases:
            with self.subTest(time_str=time_str, expected=expected, desc=description):
                with_time = dt.with_time(time_str)
                self.assertEqual(with_time.as_debug(), expected)


if __name__ == "__main__":
    unittest.main()
