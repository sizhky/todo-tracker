import re
import pytz
from datetime import datetime, timedelta
from typing import Union, Optional, Literal, Tuple


class DT:
    """
    DateTime utility class that provides conversions between natural language dates, debug format,
    and strict datetime objects.

    Three main formats are supported:
    1. Natural dates: "tomorrow evening", "next Monday", etc.
    2. Debug dates: "202505141900" (YYYYMMDDHHMM)
    3. Strict dates: Python datetime objects
    """

    # Time label mappings
    TIME_LABELS = {
        "early morning": (4, 0, 7, 59),  # 04:00-07:59
        "morning": (8, 0, 10, 59),  # 08:00-10:59
        "late morning": (11, 0, 11, 59),  # 11:00-11:59
        "noon": (12, 0, 12, 29),  # 12:00-12:29
        "early afternoon": (12, 30, 13, 59),  # 12:30-13:59
        "afternoon": (14, 0, 16, 59),  # 14:00-16:59
        "early evening": (17, 0, 18, 29),  # 17:00-18:29
        "evening": (18, 30, 20, 59),  # 18:30-20:59
        "late evening": (21, 0, 21, 59),  # 21:00-21:59
        "night": (22, 0, 23, 29),  # 22:00-23:29
        "late night": (23, 30, 0, 59),  # 23:30-00:59
        "past midnight": (1, 0, 3, 59),  # 01:00-03:59
    }

    # Time label shortcuts
    TIME_SHORTCUTS = {
        "morning": "08:00",
        "noon": "12:00",
        "afternoon": "14:00",
        "evening": "18:30",
        "night": "22:00",
        "tonight": "22:00",
    }

    def __init__(self, date_string: str, now: Optional[datetime] = None):
        """
        Initialize a DT object from a string representation.

        Args:
            date_string: A string representation of a date/time in any supported format
            now: Reference datetime for relative times. Defaults to the current time.

        Raises:
            ValueError: If the input string cannot be parsed into a valid datetime
        """
        self.original_string = date_string
        self._now = now or datetime.now().replace(microsecond=0)

        # Try to parse the input in various formats
        self._dt = self._parse_string(date_string)

        if self._dt is None:
            raise ValueError(f"Unable to parse datetime from: {date_string}")

    def _parse_string(self, date_string: str) -> Optional[datetime]:
        """
        Parse a string into a datetime object using various methods.

        Args:
            date_string: The string to parse

        Returns:
            A datetime object or None if parsing fails
        """
        # Try to parse debug format first (most explicit)
        dt = self._parse_debug_format(date_string)
        if dt:
            return dt

        # Try to parse natural language
        dt = self._parse_natural_language(date_string)
        if dt:
            return dt

        # If all parsers fail, return None
        return None

    def _parse_debug_format(self, date_string: str) -> Optional[datetime]:
        """
        Parse debug format strings like:
        - YYYYMMDDHHMM (full)
        - YYYYMMDD (date only, assumes 00:00)
        - HHMM (time only, assumes today)
        - HH (hour only, assumes today and :00 minutes)

        Args:
            date_string: The debug format string

        Returns:
            A datetime object or None if the string doesn't match debug format
        """
        # Full format: YYYYMMDDHHMM
        if re.match(r"^\d{12}$", date_string):
            year = int(date_string[0:4])
            month = int(date_string[4:6])
            day = int(date_string[6:8])
            hour = int(date_string[8:10])
            minute = int(date_string[10:12])

            return datetime(year, month, day, hour, minute)

        # Date only: YYYYMMDD
        elif re.match(r"^\d{8}$", date_string):
            year = int(date_string[0:4])
            month = int(date_string[4:6])
            day = int(date_string[6:8])

            return datetime(year, month, day, 0, 0)

        # Time only: HHMM
        elif re.match(r"^\d{4}$", date_string):
            hour = int(date_string[0:2])
            minute = int(date_string[2:4])

            return self._now.replace(hour=hour, minute=minute)

        # Hour only: HH
        elif re.match(r"^\d{2}$", date_string):
            hour = int(date_string)

            return self._now.replace(hour=hour, minute=0)

        return None

    from torch_snippets import io

    @io(level="trace")
    def _parse_natural_language(self, date_string: str) -> Optional[datetime]:
        """
        Parse natural language date expressions.

        Args:
            date_string: The natural language string

        Returns:
            A datetime object or None if parsing fails

        Raises:
            ValueError: If the input has contradictory or invalid terms
        """
        # Check for contradictory terms
        if "tomorrow" in date_string and "yesterday" in date_string:
            raise ValueError(f"Contradictory date terms in: {date_string}")

        # Simple time shortcuts
        if date_string in self.TIME_SHORTCUTS:
            time_parts = self.TIME_SHORTCUTS[date_string].split(":")
            hour, minute = int(time_parts[0]), int(time_parts[1])
            return self._now.replace(hour=hour, minute=minute)

        # Today at specific time
        if date_string == "tonight":
            return self._now.replace(hour=22, minute=0)

        # Tomorrow expressions
        if "tomorrow" in date_string:
            dt = self._now + timedelta(days=1)

            if "morning" in date_string:
                dt = dt.replace(hour=8, minute=0)
            elif "afternoon" in date_string:
                dt = dt.replace(hour=14, minute=0)
            elif "evening" in date_string:
                dt = dt.replace(hour=19, minute=0)

            return dt

        # This + time period expressions
        if date_string.startswith("this "):
            time_part = date_string[5:]
            if time_part in self.TIME_SHORTCUTS:
                time_value = self.TIME_SHORTCUTS[time_part]
                hour, minute = map(int, time_value.split(":"))
                return self._now.replace(hour=hour, minute=minute)

        # Various other natural language expressions could be added here
        # For a complete implementation, a more sophisticated NLP approach or a
        # dedicated library like dateparser would be used

        return None

    def as_debug(self) -> str:
        """
        Return the datetime in debug format: YYYYMMDDHHMM

        Returns:
            String in debug format
        """
        return self._dt.strftime("%Y%m%d%H%M")

    def as_strict(
        self, format: Literal["object", "iso"] = "object"
    ) -> Union[datetime, str]:
        """
        Return the datetime as a strict datetime object or ISO formatted string.

        Args:
            format: 'object' for datetime object, 'iso' for ISO formatted string

        Returns:
            A datetime object or ISO string
        """
        if format == "iso":
            # Return ISO format with timezone
            tz = pytz.timezone(
                "Asia/Kolkata"
            )  # Using IST as an example, should be configurable
            dt_with_tz = tz.localize(self._dt)
            return dt_with_tz.isoformat()

        return self._dt

    def _get_time_label(self) -> Tuple[str, str]:
        """
        Determine the natural time label for the current datetime.

        Returns:
            Tuple of (time_label, formatted_time)
        """
        hour = self._dt.hour
        minute = self._dt.minute

        # Handle special case for times after midnight but before 4am
        if 1 <= hour < 4:
            return "early morning (next day)", self._format_time(hour, minute)

        # Check each time label range
        for label, (start_h, start_m, end_h, end_m) in self.TIME_LABELS.items():
            # Handle ranges that cross midnight
            if start_h > end_h:
                if (hour > start_h or (hour == start_h and minute >= start_m)) or (
                    hour < end_h or (hour == end_h and minute <= end_m)
                ):
                    return label, self._format_time(hour, minute)
            # Normal ranges
            elif (hour > start_h or (hour == start_h and minute >= start_m)) and (
                hour < end_h or (hour == end_h and minute <= end_m)
            ):
                return label, self._format_time(hour, minute)

        # Fallback
        return "time", self._format_time(hour, minute)

    def _format_time(self, hour: int, minute: int) -> str:
        """Format hour and minute in 12-hour format with am/pm"""
        if hour == 0:
            h = 12
            suffix = "am"
        elif hour < 12:
            h = hour
            suffix = "am"
        elif hour == 12:
            h = 12
            suffix = "pm"
        else:
            h = hour - 12
            suffix = "pm"

        if minute == 0:
            return f"{h}{suffix}"
        else:
            return f"{h}:{minute:02d}{suffix}"

    def as_natural(self) -> str:
        """
        Return the datetime as a natural language expression.

        Returns:
            String with natural description
        """
        # For simplicity, we'll focus on the time of day descriptions as per specs
        time_label, _ = self._get_time_label()

        # Determine day reference (today, tomorrow, etc.)
        days_diff = (self._dt.date() - self._now.date()).days

        if days_diff == 0:
            day_ref = ""  # No prefix for today's time labels in basic form
        elif days_diff == 1:
            day_ref = "tomorrow"
        else:
            # Most complex natural expressions omitted for brevity
            # Would include "next Friday", "in 2 weeks", etc.
            day_ref = ""

        if time_label in ["night", "tonight"]:
            return "tonight"  # Special case

        if time_label.startswith("early morning") and days_diff > 0:
            return time_label  # Already includes "next day" for early AM hours

        return f"{day_ref} {time_label}".strip()  # Use strip to handle empty day_ref

    def as_natural_verbose(self) -> str:
        """
        Return a more detailed natural language expression with time.

        Returns:
            Verbose natural description with time
        """
        # Get base natural expression
        base_expr = self.as_natural()
        time_label, formatted_time = self._get_time_label()

        # For day expressions
        days_diff = (self._dt.date() - self._now.date()).days

        # Past times
        if days_diff < 0:
            if days_diff == -1:
                prefix = "yesterday"
            elif days_diff == -2:
                prefix = "day before yesterday"
            elif days_diff > -7 and self._dt.weekday() < self._now.weekday():
                prefix = f"last {self._dt.strftime('%A')}"
            elif days_diff > -14 and days_diff <= -7:
                prefix = "last week"
            elif days_diff > -30 and days_diff <= -14:
                weeks = abs(days_diff) // 7
                prefix = f"{weeks} weeks ago, {self._dt.strftime('%A')}"
            elif days_diff > -365 and days_diff <= -30:
                months = abs(days_diff) // 30
                if months == 1:
                    prefix = "last month"
                else:
                    prefix = f"{months} months ago"
                return f"{prefix}, {self._dt.day}th at {formatted_time}"
            else:
                years = abs(days_diff) // 365
                if years == 1:
                    prefix = "last year"
                else:
                    prefix = f"{years} years ago"
                return f"{prefix}, {self._dt.day}th {self._dt.strftime('%B')} at {formatted_time}"

            # Don't include the time label for past expressions, just the prefix and formatted time
            return f"{prefix}, {formatted_time}"

        # Future times
        elif days_diff > 0:
            if days_diff == 1:
                prefix = "tomorrow"
            elif days_diff == 2:
                prefix = "day after tomorrow"
            elif days_diff < 7 and self._dt.weekday() > self._now.weekday():
                prefix = f"this {self._dt.strftime('%A')}"
            elif days_diff >= 7 and days_diff < 14:
                prefix = f"next {self._dt.strftime('%A')}"
            elif days_diff >= 14 and days_diff < 30:
                weeks = days_diff // 7
                prefix = f"in {weeks} weeks, {self._dt.strftime('%A')}"
            elif days_diff >= 30 and days_diff < 365:
                months = days_diff // 30
                if months == 1:
                    prefix = "next month"
                else:
                    prefix = f"in {months} months"
                return f"{prefix}, {self._dt.day}th at {formatted_time}"
            else:
                years = days_diff // 365
                if years == 1:
                    prefix = "next year"
                else:
                    prefix = f"in {years} years"
                return f"{prefix}, {self._dt.day}th {self._dt.strftime('%B')} at {formatted_time}"

            # Include the time label only for "tomorrow", omit for other prefixes
            if prefix == "tomorrow":
                return f"{prefix} {time_label.replace('this ', '')}, {formatted_time}"
            else:
                return f"{prefix}, {formatted_time}"

        # Today
        return f"{base_expr}, {formatted_time}"

    def shift(self, days=0, hours=0, minutes=0) -> "DT":
        """
        Return a new DT object shifted by the specified amount.

        Args:
            days: Number of days to shift
            hours: Number of hours to shift
            minutes: Number of minutes to shift

        Returns:
            New DT instance with shifted datetime
        """
        new_dt = self._dt + timedelta(days=days, hours=hours, minutes=minutes)

        # Create a new instance with the same now reference
        result = DT(new_dt.strftime("%Y%m%d%H%M"), now=self._now)
        return result

    def with_time(self, time_str: str) -> "DT":
        """
        Return a new DT object with the specified time but same date.

        Args:
            time_str: Time string (e.g. "10:30", "10am", "10pm")

        Returns:
            New DT instance with updated time
        """
        hour, minute = 0, 0

        # Handle formats like "10am", "10pm"
        if time_str.endswith(("am", "pm")):
            is_pm = time_str.endswith("pm")
            time_val = time_str[:-2].strip()

            if ":" in time_val:
                h, m = time_val.split(":")
                hour, minute = int(h), int(m)
            else:
                hour, minute = int(time_val), 0

            if is_pm and hour < 12:
                hour += 12
            elif not is_pm and hour == 12:
                hour = 0

        # Handle 24-hour format like "10:30"
        elif ":" in time_str:
            h, m = time_str.split(":")
            hour, minute = int(h), int(m)

        # Handle hour-only like "10" (assumes 24-hour format)
        else:
            hour = int(time_str)

        new_dt = self._dt.replace(hour=hour, minute=minute)
        result = DT(new_dt.strftime("%Y%m%d%H%M"), now=self._now)
        return result

    # Property shortcuts
    @property
    def d(self) -> str:
        """Shorthand for as_debug()"""
        return self.as_debug()

    @property
    def s(self) -> datetime:
        """Shorthand for as_strict()"""
        return self.as_strict()

    @property
    def n(self) -> str:
        """Shorthand for as_natural()"""
        return self.as_natural()

    @property
    def nv(self) -> str:
        """Shorthand for as_natural_verbose()"""
        return self.as_natural_verbose()
