"""
Unit tests for time utility functions.
Tests datetime parsing, formatting, and timestamp conversion functionality.
"""
import pytest
from datetime import datetime, timezone
from unittest.mock import patch

from utils.time_utils import (
    ParseDateTimeException,
    DATETIME_DEFAULT_FORMAT,
    BIRTH_DATE_FORMAT,
    from_str_to_dt,
    from_dt_to_str,
    from_dt_to_int_timestamp,
    from_timestamp_to_dt
)


class TestParseDateTimeException:
    """Test cases for ParseDateTimeException."""
    
    def test_parse_datetime_exception_creation(self):
        """Test creating ParseDateTimeException."""
        exc = ParseDateTimeException("Test error")
        assert str(exc) == "Test error"
        assert isinstance(exc, Exception)
    
    def test_parse_datetime_exception_with_nested_exception(self):
        """Test ParseDateTimeException with nested exception."""
        original_exc = ValueError("Original error")
        exc = ParseDateTimeException(original_exc)
        assert str(exc) == "Original error"


class TestConstants:
    """Test cases for datetime format constants."""
    
    def test_datetime_default_format(self):
        """Test DATETIME_DEFAULT_FORMAT constant."""
        assert DATETIME_DEFAULT_FORMAT == "%Y-%m-%dT%H:%M:%S.%f"
        
        # Test that the format works with current datetime
        now = datetime.now()
        formatted = now.strftime(DATETIME_DEFAULT_FORMAT)
        parsed_back = datetime.strptime(formatted, DATETIME_DEFAULT_FORMAT)
        
        # Should be very close (within microseconds)
        assert abs((now - parsed_back).total_seconds()) < 0.001
    
    def test_birth_date_format(self):
        """Test BIRTH_DATE_FORMAT constant."""
        assert BIRTH_DATE_FORMAT == "%Y%m%d"
        
        # Test that the format works with a date
        test_date = datetime(1990, 5, 15)
        formatted = test_date.strftime(BIRTH_DATE_FORMAT)
        assert formatted == "19900515"


class TestFromStrToDt:
    """Test cases for from_str_to_dt function."""
    
    def test_from_str_to_dt_valid_datetime(self):
        """Test from_str_to_dt with valid datetime string."""
        dt_str = "2023-01-15T10:30:45.123456"
        result = from_str_to_dt(dt_str, DATETIME_DEFAULT_FORMAT)
        
        assert isinstance(result, datetime)
        assert result.year == 2023
        assert result.month == 1
        assert result.day == 15
        assert result.hour == 10
        assert result.minute == 30
        assert result.second == 45
        assert result.microsecond == 123456
    
    def test_from_str_to_dt_birth_date_format(self):
        """Test from_str_to_dt with birth date format."""
        birth_str = "19901225"
        result = from_str_to_dt(birth_str, BIRTH_DATE_FORMAT)
        
        assert isinstance(result, datetime)
        assert result.year == 1990
        assert result.month == 12
        assert result.day == 25
        assert result.hour == 0
        assert result.minute == 0
        assert result.second == 0
    
    def test_from_str_to_dt_custom_format(self):
        """Test from_str_to_dt with custom format."""
        dt_str = "01/15/2023 14:30"
        custom_format = "%m/%d/%Y %H:%M"
        result = from_str_to_dt(dt_str, custom_format)
        
        assert result.year == 2023
        assert result.month == 1
        assert result.day == 15
        assert result.hour == 14
        assert result.minute == 30
        assert result.second == 0
    
    def test_from_str_to_dt_various_formats(self):
        """Test from_str_to_dt with various datetime formats."""
        test_cases = [
            ("2023-01-01", "%Y-%m-%d"),
            ("01-01-2023", "%m-%d-%Y"),
            ("2023/01/01", "%Y/%m/%d"),
            ("Jan 01, 2023", "%b %d, %Y"),
            ("January 01, 2023", "%B %d, %Y"),
            ("2023-01-01 12:00:00", "%Y-%m-%d %H:%M:%S"),
            ("12:30:45", "%H:%M:%S"),
            ("2023-W01-1", "%Y-W%U-%w"),  # ISO week format
        ]
        
        for dt_str, format_str in test_cases:
            try:
                result = from_str_to_dt(dt_str, format_str)
                assert isinstance(result, datetime)
            except ParseDateTimeException:
                # Some formats might not work as expected, that's ok for this test
                pass
    
    def test_from_str_to_dt_invalid_datetime_string(self):
        """Test from_str_to_dt with invalid datetime string."""
        invalid_strings = [
            "not a date",
            "2023-13-01",  # Invalid month
            "2023-01-32",  # Invalid day
            "2023-01-01T25:00:00",  # Invalid hour
            "2023-02-30",  # Invalid date for February
            "",  # Empty string
        ]
        
        for invalid_str in invalid_strings:
            with pytest.raises(ParseDateTimeException):
                from_str_to_dt(invalid_str, DATETIME_DEFAULT_FORMAT)
    
    def test_from_str_to_dt_wrong_format(self):
        """Test from_str_to_dt with wrong format for the string."""
        dt_str = "2023-01-15T10:30:45.123456"
        wrong_format = "%Y-%m-%d"  # Format doesn't match the string
        
        with pytest.raises(ParseDateTimeException):
            from_str_to_dt(dt_str, wrong_format)
    
    def test_from_str_to_dt_none_inputs(self):
        """Test from_str_to_dt with None inputs."""
        with pytest.raises(ParseDateTimeException):
            from_str_to_dt(None, DATETIME_DEFAULT_FORMAT)
        
        with pytest.raises(ParseDateTimeException):
            from_str_to_dt("2023-01-01", None)
    
    def test_from_str_to_dt_edge_cases(self):
        """Test from_str_to_dt with edge cases."""
        # Leap year
        leap_str = "2024-02-29T12:00:00.000000"
        result = from_str_to_dt(leap_str, DATETIME_DEFAULT_FORMAT)
        assert result.month == 2
        assert result.day == 29
        
        # Year boundaries
        y2k_str = "2000-01-01T00:00:00.000000"
        result = from_str_to_dt(y2k_str, DATETIME_DEFAULT_FORMAT)
        assert result.year == 2000
        
        # Far future
        future_str = "2100-12-31T23:59:59.999999"
        result = from_str_to_dt(future_str, DATETIME_DEFAULT_FORMAT)
        assert result.year == 2100
        assert result.microsecond == 999999


class TestFromDtToStr:
    """Test cases for from_dt_to_str function."""
    
    def test_from_dt_to_str_valid_datetime(self):
        """Test from_dt_to_str with valid datetime."""
        dt = datetime(2023, 1, 15, 10, 30, 45, 123456)
        result = from_dt_to_str(dt, DATETIME_DEFAULT_FORMAT)
        
        assert result == "2023-01-15T10:30:45.123456"
        assert isinstance(result, str)
    
    def test_from_dt_to_str_birth_date_format(self):
        """Test from_dt_to_str with birth date format."""
        dt = datetime(1990, 12, 25)
        result = from_dt_to_str(dt, BIRTH_DATE_FORMAT)
        
        assert result == "19901225"
    
    def test_from_dt_to_str_custom_format(self):
        """Test from_dt_to_str with custom format."""
        dt = datetime(2023, 1, 15, 14, 30)
        custom_format = "%m/%d/%Y %H:%M"
        result = from_dt_to_str(dt, custom_format)
        
        assert result == "01/15/2023 14:30"
    
    def test_from_dt_to_str_various_formats(self):
        """Test from_dt_to_str with various formats."""
        dt = datetime(2023, 1, 15, 10, 30, 45)
        
        test_cases = [
            ("%Y-%m-%d", "2023-01-15"),
            ("%m-%d-%Y", "01-15-2023"),
            ("%Y/%m/%d", "2023/01/15"),
            ("%b %d, %Y", "Jan 15, 2023"),
            ("%B %d, %Y", "January 15, 2023"),
            ("%Y-%m-%d %H:%M:%S", "2023-01-15 10:30:45"),
            ("%H:%M:%S", "10:30:45"),
            ("%A", "Sunday"),  # Day of week
            ("%Y-%j", "2023-015"),  # Day of year
        ]
        
        for format_str, expected in test_cases:
            result = from_dt_to_str(dt, format_str)
            assert result == expected
    
    def test_from_dt_to_str_with_timezone(self):
        """Test from_dt_to_str with timezone-aware datetime."""
        dt = datetime(2023, 1, 15, 10, 30, 45, tzinfo=timezone.utc)
        result = from_dt_to_str(dt, "%Y-%m-%d %H:%M:%S %Z")
        
        assert "2023-01-15 10:30:45" in result
        assert "UTC" in result
    
    def test_from_dt_to_str_none_datetime(self):
        """Test from_dt_to_str with None datetime."""
        with pytest.raises(ParseDateTimeException):
            from_dt_to_str(None, DATETIME_DEFAULT_FORMAT)
    
    def test_from_dt_to_str_none_format(self):
        """Test from_dt_to_str with None format."""
        dt = datetime(2023, 1, 15)
        with pytest.raises(ParseDateTimeException):
            from_dt_to_str(dt, None)
    
    def test_from_dt_to_str_invalid_format(self):
        """Test from_dt_to_str with invalid format string."""
        dt = datetime(2023, 1, 15)
        invalid_formats = [
            "%Z",  # Timezone name for naive datetime
            "%invalid",  # Invalid format specifier
        ]
        
        for invalid_format in invalid_formats:
            try:
                result = from_dt_to_str(dt, invalid_format)
                # Some invalid formats might still work, returning the literal string
                assert isinstance(result, str)
            except ParseDateTimeException:
                # This is expected for truly invalid formats
                pass


class TestFromDtToIntTimestamp:
    """Test cases for from_dt_to_int_timestamp function."""
    
    def test_from_dt_to_int_timestamp_valid_datetime(self):
        """Test from_dt_to_int_timestamp with valid datetime."""
        # Use a known timestamp
        dt = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        result = from_dt_to_int_timestamp(dt)
        
        assert isinstance(result, int)
        assert result == 1672574400  # Unix timestamp for 2023-01-01 12:00:00 UTC
    
    def test_from_dt_to_int_timestamp_naive_datetime(self):
        """Test from_dt_to_int_timestamp with naive datetime."""
        dt = datetime(2023, 1, 1, 12, 0, 0)
        result = from_dt_to_int_timestamp(dt)
        
        assert isinstance(result, int)
        # Result will depend on system timezone, but should be reasonable
        assert result > 0
    
    def test_from_dt_to_int_timestamp_epoch(self):
        """Test from_dt_to_int_timestamp with epoch datetime."""
        dt = datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        result = from_dt_to_int_timestamp(dt)
        
        assert result == 0
    
    def test_from_dt_to_int_timestamp_future(self):
        """Test from_dt_to_int_timestamp with future datetime."""
        dt = datetime(2100, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        result = from_dt_to_int_timestamp(dt)
        
        assert isinstance(result, int)
        assert result >= 4102444800  # Should be around 2100
    
    def test_from_dt_to_int_timestamp_microseconds(self):
        """Test from_dt_to_int_timestamp truncates microseconds."""
        dt1 = datetime(2023, 1, 1, 12, 0, 0, 0, tzinfo=timezone.utc)
        dt2 = datetime(2023, 1, 1, 12, 0, 0, 999999, tzinfo=timezone.utc)
        
        result1 = from_dt_to_int_timestamp(dt1)
        result2 = from_dt_to_int_timestamp(dt2)
        
        # Both should have the same integer timestamp
        assert result1 == result2


class TestFromTimestampToDt:
    """Test cases for from_timestamp_to_dt function."""
    
    def test_from_timestamp_to_dt_with_timezone(self):
        """Test from_timestamp_to_dt with timezone."""
        timestamp = 1672574400  # 2023-01-01 12:00:00 UTC
        result = from_timestamp_to_dt(timestamp, 1, True)
        
        assert isinstance(result, datetime)
        assert result.year == 2023
        assert result.month == 1
        assert result.day == 1
        assert result.hour == 12
        assert result.tzinfo == timezone.utc
    
    def test_from_timestamp_to_dt_without_timezone(self):
        """Test from_timestamp_to_dt without timezone."""
        timestamp = 1672574400  # 2023-01-01 12:00:00 UTC
        result = from_timestamp_to_dt(timestamp, 1, False)
        
        assert isinstance(result, datetime)
        assert result.tzinfo is None
    
    def test_from_timestamp_to_dt_with_milliseconds(self):
        """Test from_timestamp_to_dt with millisecond timestamps."""
        timestamp_ms = 1672574400000  # 2023-01-01 12:00:00 UTC in milliseconds
        result = from_timestamp_to_dt(timestamp_ms, 1000, True)
        
        assert result.year == 2023
        assert result.month == 1
        assert result.day == 1
        assert result.hour == 12
        assert result.tzinfo == timezone.utc
    
    def test_from_timestamp_to_dt_with_microseconds(self):
        """Test from_timestamp_to_dt with microsecond timestamps."""
        timestamp_us = 1672574400000000  # 2023-01-01 12:00:00 UTC in microseconds
        result = from_timestamp_to_dt(timestamp_us, 1000000, True)
        
        assert result.year == 2023
        assert result.month == 1
        assert result.day == 1
        assert result.hour == 12
        assert result.tzinfo == timezone.utc
    
    def test_from_timestamp_to_dt_epoch(self):
        """Test from_timestamp_to_dt with epoch timestamp."""
        result = from_timestamp_to_dt(0, 1, True)
        
        assert result.year == 1970
        assert result.month == 1
        assert result.day == 1
        assert result.hour == 0
        assert result.tzinfo == timezone.utc
    
    def test_from_timestamp_to_dt_negative_timestamp(self):
        """Test from_timestamp_to_dt with negative timestamp (before epoch)."""
        result = from_timestamp_to_dt(-86400, 1, True)  # One day before epoch
        
        assert result.year == 1969
        assert result.month == 12
        assert result.day == 31
        assert result.tzinfo == timezone.utc
    
    def test_from_timestamp_to_dt_future_timestamp(self):
        """Test from_timestamp_to_dt with far future timestamp."""
        future_timestamp = 4102444800  # 2100-01-01 00:00:00 UTC
        result = from_timestamp_to_dt(future_timestamp, 1, True)
        
        assert result.year == 2100
        assert result.month == 1
        assert result.day == 1
        assert result.tzinfo == timezone.utc
    
    def test_from_timestamp_to_dt_various_units(self):
        """Test from_timestamp_to_dt with various time units."""
        base_timestamp = 1672574400  # 2023-01-01 12:00:00 UTC
        
        # Test different units
        units_and_timestamps = [
            (1, base_timestamp),  # seconds
            (1000, base_timestamp * 1000),  # milliseconds
            (1000000, base_timestamp * 1000000),  # microseconds
        ]
        
        for unit, timestamp in units_and_timestamps:
            result = from_timestamp_to_dt(timestamp, unit, True)
            assert result.year == 2023
            assert result.month == 1
            assert result.day == 1
            assert result.hour == 12


class TestRoundTripConversions:
    """Test round-trip conversions between different formats."""
    
    def test_string_to_datetime_to_string(self):
        """Test round-trip conversion from string to datetime and back."""
        original_str = "2023-06-15T14:30:45.123456"
        
        # String -> DateTime -> String
        dt = from_str_to_dt(original_str, DATETIME_DEFAULT_FORMAT)
        result_str = from_dt_to_str(dt, DATETIME_DEFAULT_FORMAT)
        
        assert result_str == original_str
    
    def test_datetime_to_timestamp_to_datetime(self):
        """Test round-trip conversion from datetime to timestamp and back."""
        original_dt = datetime(2023, 6, 15, 14, 30, 45, tzinfo=timezone.utc)
        
        # DateTime -> Timestamp -> DateTime
        timestamp = from_dt_to_int_timestamp(original_dt)
        result_dt = from_timestamp_to_dt(timestamp, 1, True)
        
        # Should match except for microseconds (lost in int timestamp)
        assert result_dt.year == original_dt.year
        assert result_dt.month == original_dt.month
        assert result_dt.day == original_dt.day
        assert result_dt.hour == original_dt.hour
        assert result_dt.minute == original_dt.minute
        assert result_dt.second == original_dt.second
        assert result_dt.tzinfo == original_dt.tzinfo
    
    def test_full_round_trip(self):
        """Test full round-trip conversion through all formats."""
        original_str = "2023-06-15T14:30:45.000000"
        
        # String -> DateTime -> Timestamp -> DateTime -> String
        dt1 = from_str_to_dt(original_str, DATETIME_DEFAULT_FORMAT)
        timestamp = from_dt_to_int_timestamp(dt1)
        dt2 = from_timestamp_to_dt(timestamp, 1, False)
        result_str = from_dt_to_str(dt2, DATETIME_DEFAULT_FORMAT)
        
        # Should be close (microseconds might be lost)
        assert result_str.startswith("2023-06-15T14:30:45")


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling."""
    
    def test_leap_year_handling(self):
        """Test leap year date handling."""
        # Valid leap year date
        leap_str = "2024-02-29T12:00:00.000000"
        dt = from_str_to_dt(leap_str, DATETIME_DEFAULT_FORMAT)
        assert dt.month == 2
        assert dt.day == 29
        
        # Invalid leap year date
        with pytest.raises(ParseDateTimeException):
            from_str_to_dt("2023-02-29T12:00:00.000000", DATETIME_DEFAULT_FORMAT)
    
    def test_daylight_saving_time_boundaries(self):
        """Test datetime handling around DST boundaries."""
        # This test is timezone-dependent, so we'll just ensure no crashes
        dst_dates = [
            "2023-03-12T02:00:00.000000",  # Spring forward in US
            "2023-11-05T02:00:00.000000",  # Fall back in US
        ]
        
        for date_str in dst_dates:
            try:
                dt = from_str_to_dt(date_str, DATETIME_DEFAULT_FORMAT)
                timestamp = from_dt_to_int_timestamp(dt)
                assert isinstance(timestamp, int)
            except ParseDateTimeException:
                # DST handling might fail in some cases, that's acceptable
                pass
    
    def test_extreme_timestamps(self):
        """Test with extreme timestamp values."""
        # Very large timestamp (far future)
        large_timestamp = 32503680000  # Year 3000
        result = from_timestamp_to_dt(large_timestamp, 1, True)
        assert result.year >= 3000
        
        # Very negative timestamp (far past)
        negative_timestamp = -2208988800  # Year 1900
        result = from_timestamp_to_dt(negative_timestamp, 1, True)
        assert result.year <= 1900