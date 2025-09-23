"""
Unit tests for User domain entities.
Tests UserEntity, UserMetadataPayload and all their associated payload classes.
"""
import uuid
from datetime import datetime, timezone
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from internal.domains.entities.user import (
    UserEntity,
    UserMetadataPayload,
    CreateUserPayload,
    UpdateUserPayload
)


class TestUserEntity:
    """Test cases for UserEntity."""
    
    def test_user_entity_creation_with_valid_data(self, sample_user_data):
        """Test creating UserEntity with valid data."""
        user = UserEntity(**sample_user_data)
        
        assert user.id_ == sample_user_data["id_"]
        assert user.username == sample_user_data["username"]
        assert user.metadata_ == sample_user_data["metadata_"]
        assert user.is_active == sample_user_data["is_active"]
        assert user.created_at == sample_user_data["created_at"]
        assert user.updated_at == sample_user_data["updated_at"]
    
    def test_user_entity_creation_with_minimal_data(self):
        """Test creating UserEntity with minimal required data."""
        user_data = {
            "id_": uuid.uuid4(),
            "username": "testuser",
            "is_active": True,
            "created_at": datetime.now(timezone.utc)
        }
        
        user = UserEntity(**user_data)
        
        assert user.id_ == user_data["id_"]
        assert user.username == user_data["username"]
        assert user.is_active == user_data["is_active"]
        assert user.created_at == user_data["created_at"]
        assert user.metadata_ is None
        assert user.updated_at is None
    
    def test_user_entity_creation_with_empty_metadata(self, sample_user_data):
        """Test creating UserEntity with empty metadata."""
        sample_user_data["metadata_"] = {}
        
        user = UserEntity(**sample_user_data)
        
        assert user.metadata_ == {}
    
    def test_user_entity_creation_without_metadata(self, sample_user_data):
        """Test creating UserEntity without metadata."""
        sample_user_data["metadata_"] = None
        
        user = UserEntity(**sample_user_data)
        
        assert user.metadata_ is None
    
    def test_user_entity_to_dict(self, sample_user_data):
        """Test UserEntity to_dict method."""
        user = UserEntity(**sample_user_data)
        user_dict = user.to_dict()
        
        assert isinstance(user_dict, dict)
        assert user_dict["id_"] == sample_user_data["id_"]
        assert user_dict["username"] == sample_user_data["username"]
        assert user_dict["metadata_"] == sample_user_data["metadata_"]
        assert user_dict["is_active"] == sample_user_data["is_active"]
    
    def test_user_entity_to_dict_exclude_none(self, sample_user_data):
        """Test UserEntity to_dict with exclude_none=True."""
        sample_user_data["updated_at"] = None
        user = UserEntity(**sample_user_data)
        user_dict = user.to_dict(exclude_none=True)
        
        assert "updated_at" not in user_dict
    
    def test_user_entity_invalid_id(self, sample_user_data):
        """Test UserEntity with invalid UUID."""
        sample_user_data["id_"] = "invalid-uuid"
        
        with pytest.raises(ValidationError):
            UserEntity(**sample_user_data)
    
    def test_user_entity_missing_required_fields(self):
        """Test UserEntity with missing required fields."""
        with pytest.raises(ValidationError):
            UserEntity()
        
        with pytest.raises(ValidationError):
            UserEntity(id_=uuid.uuid4())
        
        with pytest.raises(ValidationError):
            UserEntity(id_=uuid.uuid4(), username="test")
    
    def test_user_entity_invalid_is_active_type(self, sample_user_data):
        """Test UserEntity with invalid is_active type."""
        sample_user_data["is_active"] = "true"  # string instead of bool
        
        # Pydantic should coerce this to boolean
        user = UserEntity(**sample_user_data)
        assert user.is_active is True
    
    def test_user_entity_with_complex_metadata(self, sample_user_data):
        """Test UserEntity with complex metadata structure."""
        complex_metadata = {
            "fullname": "John Doe",
            "dob": "1990-01-01",
            "address": {
                "street": "123 Main St",
                "city": "Anytown",
                "country": "US"
            },
            "preferences": {
                "theme": "dark",
                "language": "en",
                "notifications": True
            }
        }
        sample_user_data["metadata_"] = complex_metadata
        
        user = UserEntity(**sample_user_data)
        assert user.metadata_ == complex_metadata


class TestUserMetadataPayload:
    """Test cases for UserMetadataPayload."""
    
    def test_metadata_payload_creation_with_valid_data(self):
        """Test creating UserMetadataPayload with valid data."""
        metadata_data = {
            "fullname": "John Doe",
            "dob": "1990-01-01"
        }
        
        metadata = UserMetadataPayload(**metadata_data)
        
        assert metadata.fullname == metadata_data["fullname"]
        assert metadata.dob == metadata_data["dob"]
    
    def test_metadata_payload_creation_with_empty_data(self):
        """Test creating UserMetadataPayload with empty data."""
        metadata = UserMetadataPayload()
        
        assert metadata.fullname is None
        assert metadata.dob is None
    
    def test_metadata_payload_creation_with_partial_data(self):
        """Test creating UserMetadataPayload with partial data."""
        metadata = UserMetadataPayload(fullname="John Doe")
        
        assert metadata.fullname == "John Doe"
        assert metadata.dob is None
    
    def test_metadata_payload_to_dict(self):
        """Test UserMetadataPayload to_dict method."""
        metadata_data = {
            "fullname": "John Doe",
            "dob": "1990-01-01"
        }
        
        metadata = UserMetadataPayload(**metadata_data)
        metadata_dict = metadata.to_dict()
        
        assert isinstance(metadata_dict, dict)
        assert metadata_dict["fullname"] == metadata_data["fullname"]
        assert metadata_dict["dob"] == metadata_data["dob"]
    
    def test_metadata_payload_to_dict_exclude_none(self):
        """Test UserMetadataPayload to_dict with exclude_none=True."""
        metadata = UserMetadataPayload(fullname="John Doe")
        metadata_dict = metadata.to_dict(exclude_none=True)
        
        assert "dob" not in metadata_dict
        assert metadata_dict["fullname"] == "John Doe"
    
    def test_metadata_payload_with_empty_strings(self):
        """Test UserMetadataPayload with empty strings."""
        metadata = UserMetadataPayload(fullname="", dob="")
        
        assert metadata.fullname == ""
        assert metadata.dob == ""
    
    def test_metadata_payload_with_whitespace_strings(self):
        """Test UserMetadataPayload with whitespace strings."""
        metadata = UserMetadataPayload(fullname="   ", dob=" \t\n ")
        
        assert metadata.fullname == "   "
        assert metadata.dob == " \t\n "


class TestCreateUserPayload:
    """Test cases for CreateUserPayload."""
    
    def test_create_payload_with_valid_data(self):
        """Test creating CreateUserPayload with valid data."""
        metadata = UserMetadataPayload(fullname="John Doe", dob="1990-01-01")
        payload_data = {
            "id_": str(uuid.uuid4()),
            "username": "johndoe",
            "metadata_": metadata,
            "created_at": "2023-01-01T12:00:00.000000",
            "updated_at": "2023-01-01T12:30:00.000000"
        }
        
        payload = CreateUserPayload(**payload_data)
        
        assert payload.id_ == payload_data["id_"]
        assert payload.username == payload_data["username"]
        assert payload.metadata_ == metadata
        assert payload.created_at == payload_data["created_at"]
        assert payload.updated_at == payload_data["updated_at"]
    
    def test_create_payload_with_empty_data(self):
        """Test creating CreateUserPayload with empty data."""
        payload = CreateUserPayload()
        
        assert payload.id_ is None
        assert payload.username is None
        assert payload.metadata_ is None
        assert payload.created_at is None
        assert payload.updated_at is None
    
    def test_create_payload_with_minimal_data(self):
        """Test creating CreateUserPayload with minimal data."""
        payload = CreateUserPayload(username="johndoe")
        
        assert payload.username == "johndoe"
        assert payload.id_ is None
        assert payload.metadata_ is None
    
    def test_create_payload_validation_valid_uuid(self):
        """Test CreateUserPayload validation with valid UUID."""
        payload = CreateUserPayload(id_=str(uuid.uuid4()))
        payload.validate_()  # Should not raise
    
    def test_create_payload_validation_invalid_uuid(self):
        """Test CreateUserPayload validation with invalid UUID."""
        payload = CreateUserPayload(id_="invalid-uuid")
        
        with pytest.raises(ValueError):
            payload.validate_()
    
    def test_create_payload_validation_valid_dates(self):
        """Test CreateUserPayload validation with valid dates."""
        payload = CreateUserPayload(
            created_at="2023-01-01T12:00:00.000000",
            updated_at="2023-01-01T12:30:00.000000"
        )
        payload.validate_()  # Should not raise
    
    def test_create_payload_validation_invalid_created_at(self):
        """Test CreateUserPayload validation with invalid created_at."""
        payload = CreateUserPayload(created_at="invalid-date")
        
        with pytest.raises(ValueError):
            payload.validate_()
    
    def test_create_payload_validation_invalid_updated_at(self):
        """Test CreateUserPayload validation with invalid updated_at."""
        payload = CreateUserPayload(updated_at="invalid-date")
        
        with pytest.raises(ValueError):
            payload.validate_()
    
    def test_create_payload_with_metadata_dict(self):
        """Test CreateUserPayload with metadata as dict."""
        metadata_dict = {"fullname": "John Doe", "dob": "1990-01-01"}
        payload = CreateUserPayload(metadata_=metadata_dict)
        
        # Pydantic should convert dict to UserMetadataPayload
        assert isinstance(payload.metadata_, UserMetadataPayload)
        assert payload.metadata_.fullname == "John Doe"
        assert payload.metadata_.dob == "1990-01-01"


class TestUpdateUserPayload:
    """Test cases for UpdateUserPayload."""
    
    def test_update_payload_with_valid_data(self):
        """Test creating UpdateUserPayload with valid data."""
        metadata = UserMetadataPayload(fullname="Jane Doe", dob="1985-05-15")
        payload_data = {
            "id_": str(uuid.uuid4()),
            "metadata_": metadata,
            "updated_at": "2023-01-01T12:30:00.000000"
        }
        
        payload = UpdateUserPayload(**payload_data)
        
        assert payload.id_ == payload_data["id_"]
        assert payload.metadata_ == metadata
        assert payload.updated_at == payload_data["updated_at"]
    
    def test_update_payload_with_empty_data(self):
        """Test creating UpdateUserPayload with empty data."""
        payload = UpdateUserPayload()
        
        assert payload.id_ is None
        assert payload.metadata_ is None
        assert payload.updated_at is None
    
    def test_update_payload_validation_valid_uuid(self):
        """Test UpdateUserPayload validation with valid UUID."""
        payload = UpdateUserPayload(id_=str(uuid.uuid4()))
        payload.validate_()  # Should not raise
    
    def test_update_payload_validation_invalid_uuid(self):
        """Test UpdateUserPayload validation with invalid UUID."""
        payload = UpdateUserPayload(id_="invalid-uuid")
        
        with pytest.raises(ValueError):
            payload.validate_()
    
    def test_update_payload_validation_valid_updated_at(self):
        """Test UpdateUserPayload validation with valid updated_at."""
        payload = UpdateUserPayload(updated_at="2023-01-01T12:30:00.000000")
        payload.validate_()  # Should not raise
    
    def test_update_payload_validation_invalid_updated_at(self):
        """Test UpdateUserPayload validation with invalid updated_at."""
        payload = UpdateUserPayload(updated_at="invalid-date")
        
        with pytest.raises(ValueError):
            payload.validate_()
    
    def test_update_payload_with_metadata_dict(self):
        """Test UpdateUserPayload with metadata as dict."""
        metadata_dict = {"fullname": "Updated Name", "dob": "1995-12-25"}
        payload = UpdateUserPayload(metadata_=metadata_dict)
        
        # Pydantic should convert dict to UserMetadataPayload
        assert isinstance(payload.metadata_, UserMetadataPayload)
        assert payload.metadata_.fullname == "Updated Name"
        assert payload.metadata_.dob == "1995-12-25"


class TestUserEntityEdgeCases:
    """Test edge cases and boundary conditions for UserEntity."""
    
    def test_user_with_very_long_username(self, sample_user_data):
        """Test UserEntity with very long username."""
        long_username = "x" * 1000  # Very long username
        sample_user_data["username"] = long_username
        
        user = UserEntity(**sample_user_data)
        assert user.username == long_username
    
    def test_user_with_empty_username(self, sample_user_data):
        """Test UserEntity with empty username."""
        sample_user_data["username"] = ""
        
        user = UserEntity(**sample_user_data)
        assert user.username == ""
    
    def test_user_with_special_characters_in_username(self, sample_user_data):
        """Test UserEntity with special characters in username."""
        special_username = "user@example.com!#$%"
        sample_user_data["username"] = special_username
        
        user = UserEntity(**sample_user_data)
        assert user.username == special_username
    
    def test_user_with_unicode_username(self, sample_user_data):
        """Test UserEntity with unicode characters in username."""
        unicode_username = "用户名_ñáéíóú_🌟"
        sample_user_data["username"] = unicode_username
        
        user = UserEntity(**sample_user_data)
        assert user.username == unicode_username
    
    def test_user_with_numeric_username(self, sample_user_data):
        """Test UserEntity with numeric username."""
        sample_user_data["username"] = "123456789"
        
        user = UserEntity(**sample_user_data)
        assert user.username == "123456789"
    
    def test_user_with_boolean_coercion_for_is_active(self, sample_user_data):
        """Test UserEntity with valid boolean coercible values for is_active."""
        # Test valid truthy values that Pydantic accepts
        truthy_values = [True, 1, "1", "true", "True", "TRUE", "yes", "Yes", "YES", "on", "On", "ON"]
        for value in truthy_values:
            sample_user_data["is_active"] = value
            user = UserEntity(**sample_user_data)
            assert user.is_active is True
        
        # Test valid falsy values that Pydantic accepts
        falsy_values = [False, 0, "0", "false", "False", "FALSE", "no", "No", "NO", "off", "Off", "OFF"]
        for value in falsy_values:
            sample_user_data["is_active"] = value
            user = UserEntity(**sample_user_data)
            assert user.is_active is False
    
    def test_user_with_invalid_boolean_values_for_is_active(self, sample_user_data):
        """Test UserEntity with invalid boolean values for is_active."""
        # Test values that should raise ValidationError
        invalid_values = [[], [1, 2, 3], {}, {"key": "value"}, "invalid", 2]
        for value in invalid_values:
            sample_user_data["is_active"] = value
            with pytest.raises(ValidationError):
                UserEntity(**sample_user_data)
    
    def test_user_with_none_metadata_vs_empty_dict(self, sample_user_data):
        """Test UserEntity with None vs empty dict metadata."""
        # Test with None
        sample_user_data["metadata_"] = None
        user1 = UserEntity(**sample_user_data)
        assert user1.metadata_ is None
        
        # Test with empty dict
        sample_user_data["metadata_"] = {}
        user2 = UserEntity(**sample_user_data)
        assert user2.metadata_ == {}
    
    def test_user_metadata_payload_with_long_values(self):
        """Test UserMetadataPayload with very long values."""
        long_name = "x" * 5000
        long_dob = "1990-01-01" + "x" * 1000  # Invalid but long
        
        metadata = UserMetadataPayload(fullname=long_name, dob=long_dob)
        
        assert metadata.fullname == long_name
        assert metadata.dob == long_dob
    
    def test_user_creation_with_future_timestamps(self, sample_user_data):
        """Test UserEntity with future timestamps."""
        future_date = datetime(2050, 1, 1, tzinfo=timezone.utc)
        sample_user_data["created_at"] = future_date
        sample_user_data["updated_at"] = future_date
        
        user = UserEntity(**sample_user_data)
        assert user.created_at == future_date
        assert user.updated_at == future_date
    
    def test_user_creation_with_very_old_timestamps(self, sample_user_data):
        """Test UserEntity with very old timestamps."""
        old_date = datetime(1900, 1, 1, tzinfo=timezone.utc)
        sample_user_data["created_at"] = old_date
        sample_user_data["updated_at"] = old_date
        
        user = UserEntity(**sample_user_data)
        assert user.created_at == old_date
        assert user.updated_at == old_date