import unittest
from datetime import datetime
from freezegun import freeze_time


@freeze_time("2025-05-13 12:00:00")  # Tuesday, May 13, 2025
class _TestWeekdays(unittest.TestCase):
    def _test_weekday_calculation(self):
        """Test weekday calculation for various dates."""
        now = datetime(2025, 5, 13, 12, 0, 0)
        print(f"Now: {now}, weekday: {now.weekday()}, strftime: {now.strftime('%A')}")

        # May 16, 2025
        date1 = datetime(2025, 5, 16, 10, 0, 0)
        print(
            f"May 16: {date1}, weekday: {date1.weekday()}, strftime: {date1.strftime('%A')}"
        )

        # May 17, 2025
        date2 = datetime(2025, 5, 17, 10, 0, 0)
        print(
            f"May 17: {date2}, weekday: {date2.weekday()}, strftime: {date2.strftime('%A')}"
        )

        # May 23, 2025
        date3 = datetime(2025, 5, 23, 10, 0, 0)
        print(
            f"May 23: {date3}, weekday: {date3.weekday()}, strftime: {date3.strftime('%A')}"
        )

        # Check which days fall within a particular week
        print("\nDays diff:")
        for i in range(1, 20):
            test_date = now.replace(day=now.day + i)
            days_diff = (test_date.date() - now.date()).days
            print(
                f"Date: {test_date.date()}, Days diff: {days_diff}, Weekday: {test_date.strftime('%A')}"
            )


if __name__ == "__main__":
    unittest.main()
