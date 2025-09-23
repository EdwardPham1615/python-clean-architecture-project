"""
Unit tests for string utility functions.
Tests JSON parsing functionality.
"""
import pytest
import orjson
from pydantic import ValidationError

from utils.string_utils import from_str_to_dict


class TestFromStrToDict:
    """Test cases for from_str_to_dict function."""
    
    def test_from_str_to_dict_valid_json(self):
        """Test from_str_to_dict with valid JSON string."""
        json_str = '{"name": "John", "age": 30, "active": true}'
        result = from_str_to_dict(json_str)
        
        expected = {"name": "John", "age": 30, "active": True}
        assert result == expected
        assert isinstance(result, dict)
    
    def test_from_str_to_dict_empty_dict(self):
        """Test from_str_to_dict with empty dictionary JSON."""
        json_str = '{}'
        result = from_str_to_dict(json_str)
        
        assert result == {}
        assert isinstance(result, dict)
    
    def test_from_str_to_dict_nested_json(self):
        """Test from_str_to_dict with nested JSON structure."""
        json_str = '''
        {
            "user": {
                "name": "John Doe",
                "metadata": {
                    "preferences": {"theme": "dark"},
                    "settings": {"notifications": true}
                }
            },
            "posts": [
                {"id": 1, "title": "First Post"},
                {"id": 2, "title": "Second Post"}
            ]
        }
        '''
        result = from_str_to_dict(json_str)
        
        assert isinstance(result, dict)
        assert "user" in result
        assert "posts" in result
        assert isinstance(result["user"], dict)
        assert isinstance(result["posts"], list)
        assert result["user"]["name"] == "John Doe"
        assert len(result["posts"]) == 2
    
    def test_from_str_to_dict_with_arrays(self):
        """Test from_str_to_dict with JSON containing arrays."""
        json_str = '{"numbers": [1, 2, 3], "names": ["Alice", "Bob", "Charlie"]}'
        result = from_str_to_dict(json_str)
        
        expected = {"numbers": [1, 2, 3], "names": ["Alice", "Bob", "Charlie"]}
        assert result == expected
        assert isinstance(result["numbers"], list)
        assert isinstance(result["names"], list)
    
    def test_from_str_to_dict_with_null_values(self):
        """Test from_str_to_dict with null values."""
        json_str = '{"name": null, "age": 25, "active": null}'
        result = from_str_to_dict(json_str)
        
        expected = {"name": None, "age": 25, "active": None}
        assert result == expected
        assert result["name"] is None
        assert result["active"] is None
    
    def test_from_str_to_dict_with_special_characters(self):
        """Test from_str_to_dict with special characters and unicode."""
        json_str = '{"message": "Hello, 世界! 🌟", "symbol": "@#$%^&*()"}'
        result = from_str_to_dict(json_str)
        
        assert result["message"] == "Hello, 世界! 🌟"
        assert result["symbol"] == "@#$%^&*()"
    
    def test_from_str_to_dict_with_escaped_characters(self):
        """Test from_str_to_dict with escaped characters."""
        json_str = '{"quote": "He said \\"Hello\\"", "newline": "Line 1\\nLine 2"}'
        result = from_str_to_dict(json_str)
        
        assert result["quote"] == 'He said "Hello"'
        assert result["newline"] == "Line 1\nLine 2"
    
    def test_from_str_to_dict_with_numbers(self):
        """Test from_str_to_dict with various number types."""
        json_str = '{"integer": 42, "float": 3.14, "negative": -10, "zero": 0}'
        result = from_str_to_dict(json_str)
        
        assert result["integer"] == 42
        assert result["float"] == 3.14
        assert result["negative"] == -10
        assert result["zero"] == 0
        assert isinstance(result["integer"], int)
        assert isinstance(result["float"], float)
    
    def test_from_str_to_dict_with_booleans(self):
        """Test from_str_to_dict with boolean values."""
        json_str = '{"is_active": true, "is_deleted": false}'
        result = from_str_to_dict(json_str)
        
        assert result["is_active"] is True
        assert result["is_deleted"] is False
        assert isinstance(result["is_active"], bool)
        assert isinstance(result["is_deleted"], bool)
    
    def test_from_str_to_dict_invalid_json(self):
        """Test from_str_to_dict with invalid JSON string."""
        invalid_json_strings = [
            '{"name": "John", "age": 30,}',  # Trailing comma
            '{"name": "John" "age": 30}',    # Missing comma
            '{name: "John"}',                # Unquoted key
            '{"name": John}',                # Unquoted string value
            '{"name": "John", "age":}',      # Missing value
            '{',                             # Incomplete JSON
            '',                              # Empty string
            'not json at all',               # Not JSON
            '{"name": "John"',               # Missing closing brace
        ]
        
        for invalid_json in invalid_json_strings:
            with pytest.raises(orjson.JSONDecodeError):
                from_str_to_dict(invalid_json)
    
    def test_from_str_to_dict_with_large_json(self):
        """Test from_str_to_dict with large JSON structure."""
        large_dict = {
            f"key_{i}": {
                "id": i,
                "name": f"Name_{i}",
                "data": list(range(10)),
                "metadata": {"created": f"2023-01-{i:02d}", "active": i % 2 == 0}
            }
            for i in range(100)
        }
        
        json_str = orjson.dumps(large_dict).decode()
        result = from_str_to_dict(json_str)
        
        assert len(result) == 100
        assert result["key_0"]["id"] == 0
        assert result["key_99"]["id"] == 99
        assert isinstance(result["key_0"]["data"], list)
    
    def test_from_str_to_dict_with_whitespace(self):
        """Test from_str_to_dict with JSON containing whitespace."""
        json_str = '''
        {
            "name"   :   "John"   ,
            "age"    :   30       ,
            "active" :   true
        }
        '''
        result = from_str_to_dict(json_str)
        
        expected = {"name": "John", "age": 30, "active": True}
        assert result == expected
    
    def test_from_str_to_dict_empty_string(self):
        """Test from_str_to_dict with empty string."""
        with pytest.raises(orjson.JSONDecodeError):
            from_str_to_dict("")
    
    def test_from_str_to_dict_none_input(self):
        """Test from_str_to_dict with None input."""
        with pytest.raises(orjson.JSONDecodeError):
            from_str_to_dict(None)
    
    def test_from_str_to_dict_non_string_input(self):
        """Test from_str_to_dict with non-string input."""
        with pytest.raises(orjson.JSONDecodeError):
            from_str_to_dict({"key": "value"})
        
        with pytest.raises(orjson.JSONDecodeError):
            from_str_to_dict(123)
        
        with pytest.raises(orjson.JSONDecodeError):
            from_str_to_dict([1, 2, 3])
    
    def test_from_str_to_dict_json_array_root(self):
        """Test from_str_to_dict with JSON array at root level."""
        json_str = '[{"name": "John"}, {"name": "Jane"}]'
        
        # orjson.loads should handle this, but it returns a list, not dict
        # The function name suggests it should return dict, so this might be unexpected
        result = from_str_to_dict(json_str)
        
        assert isinstance(result, list)  # orjson.loads returns the actual structure
        assert len(result) == 2
        assert result[0]["name"] == "John"
        assert result[1]["name"] == "Jane"
    
    def test_from_str_to_dict_with_datetime_strings(self):
        """Test from_str_to_dict with datetime-like strings."""
        json_str = '''
        {
            "created_at": "2023-01-01T12:00:00.000Z",
            "updated_at": "2023-12-31T23:59:59.999Z",
            "date": "2023-06-15"
        }
        '''
        result = from_str_to_dict(json_str)
        
        # orjson doesn't automatically parse datetime strings - they remain as strings
        assert isinstance(result["created_at"], str)
        assert isinstance(result["updated_at"], str)
        assert isinstance(result["date"], str)
        assert result["created_at"] == "2023-01-01T12:00:00.000Z"
        assert result["date"] == "2023-06-15"