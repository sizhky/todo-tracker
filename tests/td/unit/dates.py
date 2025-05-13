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
        # Full YYYYMMDDHHMM format
        dt = DT("202505141900")
        self.assertEqual(dt.as_debug(), "202505141900")

        # YYYYMMDD format (assumes 00:00)
        dt = DT("20250513")
        self.assertEqual(dt.as_debug(), "202505130000")

        # HHMM format (assumes today)
        dt = DT("1730")
        self.assertEqual(dt.as_debug(), "202505131730")

        # HH format (assumes today at :00)
        dt = DT("17")
        self.assertEqual(dt.as_debug(), "202505131700")

    def test_natural_format_parsing(self):
        """Test parsing of natural language date expressions."""
        # Simple cases
        self.assertEqual(DT("tonight").as_debug(), "202505132200")
        self.assertEqual(
            DT("this evening").as_debug(), "202505131830"
        )  # Using the 18:30 definition
        self.assertEqual(DT("tomorrow morning").as_debug(), "202505140800")

    def test_as_strict(self):
        """Test conversion to strict format."""
        # Test the object format
        dt = DT("202505131730")
        self.assertEqual(dt.as_strict(), datetime(2025, 5, 13, 17, 30))

        # Test the ISO format with timezone
        iso_string = dt.as_strict(format="iso")
        self.assertTrue(iso_string.startswith("2025-05-13T17:30:00+"))

    def test_invalid_input(self):
        """Test handling of invalid input."""
        with self.assertRaises(ValueError):
            DT("tomorrow yesterday")

        with self.assertRaises(ValueError):
            DT("Feb 30")

    def test_natural_expressions(self):
        """Test conversion to natural expressions."""
        self.assertEqual(DT("202505130800").n, "this morning")
        self.assertEqual(DT("202505131059").n, "this morning")
        self.assertEqual(DT("202505131100").n, "late morning")
        self.assertEqual(DT("202505131200").n, "noon")
        self.assertEqual(DT("202505131230").n, "early afternoon")
        self.assertEqual(DT("202505131400").n, "this afternoon")
        self.assertEqual(DT("202505131700").n, "early evening")
        self.assertEqual(DT("202505131830").n, "this evening")
        self.assertEqual(DT("202505132100").n, "late evening")
        self.assertEqual(DT("202505132200").n, "tonight")
        self.assertEqual(DT("202505132330").n, "late night")
        self.assertEqual(DT("202505140100").n, "early morning (next day)")

    def test_natural_verbose_expressions(self):
        """Test conversion to verbose natural expressions."""
        # Today/Current time expressions
        self.assertEqual(DT("202505130800").nv, "this morning, 8am")
        self.assertEqual(DT("202505131059").nv, "this morning, 10:59am")
        self.assertEqual(DT("202505131100").nv, "late morning, 11am")
        self.assertEqual(DT("202505131200").nv, "noon, 12pm")

        # Future expressions
        self.assertEqual(DT("202505140800").nv, "tomorrow morning, 8am")
        self.assertEqual(DT("202505150800").nv, "day after tomorrow, 8am")
        self.assertEqual(DT("202505161000").nv, "this Thursday, 10am")
        self.assertEqual(DT("202505171000").nv, "this Friday, 10am")
        self.assertEqual(DT("202505231000").nv, "next Thursday, 10am")
        self.assertEqual(DT("202506041000").nv, "in 3 weeks, Tuesday 10am")
        self.assertEqual(DT("202506131000").nv, "next month, 13th at 10am")
        self.assertEqual(DT("202507131000").nv, "in 2 months, 13th at 10am")
        self.assertEqual(DT("202605131000").nv, "next year, 13th May at 10am")

        # Past expressions
        self.assertEqual(DT("202505120800").nv, "yesterday morning, 8am")
        self.assertEqual(DT("202505110800").nv, "day before yesterday, 8am")
        self.assertEqual(DT("202505091000").nv, "last Thursday, 10am")
        self.assertEqual(DT("202504131000").nv, "last month, 13th at 10am")
        self.assertEqual(DT("202503131000").nv, "2 months ago, 13th at 10am")
        self.assertEqual(DT("202405131000").nv, "last year, 13th May at 10am")

    def test_shift_method(self):
        """Test shifting a datetime."""
        dt = DT("202505131200")  # noon today

        # Shift forward
        shifted = dt.shift(days=1, hours=2, minutes=30)
        self.assertEqual(shifted.as_debug(), "202505141430")  # tomorrow at 2:30 PM

        # Shift backward
        shifted = dt.shift(days=-1, hours=-2, minutes=-30)
        self.assertEqual(shifted.as_debug(), "202505120930")  # yesterday at 9:30 AM

    def test_with_time_method(self):
        """Test changing the time of a datetime."""
        dt = DT("20250513")  # today at midnight

        # 12-hour format
        with_time = dt.with_time("10:30am")
        self.assertEqual(with_time.as_debug(), "202505131030")

        with_time = dt.with_time("2:45pm")
        self.assertEqual(with_time.as_debug(), "202505131445")

        # 24-hour format
        with_time = dt.with_time("22:15")
        self.assertEqual(with_time.as_debug(), "202505132215")

        # Hour-only
        with_time = dt.with_time("14")
        self.assertEqual(with_time.as_debug(), "202505131400")


if __name__ == "__main__":
    unittest.main()
