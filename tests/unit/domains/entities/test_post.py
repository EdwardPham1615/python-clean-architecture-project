"""
Unit tests for Post domain entities.
Tests PostEntity and all its associated payload classes.
"""
import uuid
from datetime import datetime, timezone
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from internal.domains.entities.post import (
    PostEntity,
    GetMultiPostsFilter,
    CreatePostPayload,
    UpdatePostPayload,
    DeletePostPayload
)
from internal.domains.entities.user import UserEntity


class TestPostEntity:
    """Test cases for PostEntity."""
    
    def test_post_entity_creation_with_valid_data(self, sample_post_data):
        """Test creating PostEntity with valid data."""
        post = PostEntity(**sample_post_data)
        
        assert post.id_ == sample_post_data["id_"]
        assert post.text_content == sample_post_data["text_content"]
        assert post.created_at == sample_post_data["created_at"]
        assert post.updated_at == sample_post_data["updated_at"]
        assert post.owner_id == sample_post_data["owner_id"]
        assert post.owner is None
    
    def test_post_entity_creation_with_owner(self, sample_post_data, sample_user_data):
        """Test creating PostEntity with owner relationship."""
        owner = UserEntity(**sample_user_data)
        sample_post_data["owner"] = owner
        
        post = PostEntity(**sample_post_data)
        
        assert post.owner == owner
        assert post.owner.id_ == sample_user_data["id_"]
    
    def test_post_entity_to_dict(self, sample_post_data):
        """Test PostEntity to_dict method."""
        post = PostEntity(**sample_post_data)
        post_dict = post.to_dict()
        
        assert isinstance(post_dict, dict)
        assert post_dict["id_"] == str(sample_post_data["id_"])
        assert post_dict["text_content"] == sample_post_data["text_content"]
        assert post_dict["owner_id"] == str(sample_post_data["owner_id"])
    
    def test_post_entity_to_dict_exclude_none(self, sample_post_data):
        """Test PostEntity to_dict with exclude_none=True."""
        post = PostEntity(**sample_post_data)
        post_dict = post.to_dict(exclude_none=True)
        
        assert "updated_at" not in post_dict
        assert "owner" not in post_dict
    
    def test_post_entity_invalid_id(self, sample_post_data):
        """Test PostEntity with invalid UUID."""
        sample_post_data["id_"] = "invalid-uuid"
        
        with pytest.raises(ValidationError):
            PostEntity(**sample_post_data)
    
    def test_post_entity_missing_required_fields(self):
        """Test PostEntity with missing required fields."""
        with pytest.raises(ValidationError):
            PostEntity()
        
        with pytest.raises(ValidationError):
            PostEntity(id_=uuid.uuid4())


class TestGetMultiPostsFilter:
    """Test cases for GetMultiPostsFilter."""
    
    def test_filter_creation_with_valid_data(self):
        """Test creating filter with valid data."""
        filter_data = {
            "sort_field": "created_at",
            "sort_order": "DESC",
            "offset": 0,
            "limit": 10,
            "from_date": "2023-01-01 00:00:00",
            "to_date": "2023-12-31 23:59:59",
            "enable_count": True,
            "owner_id": str(uuid.uuid4())
        }
        
        filter_obj = GetMultiPostsFilter(**filter_data)
        
        assert filter_obj.sort_field == "created_at"
        assert filter_obj.sort_order == "DESC"
        assert filter_obj.offset == 0
        assert filter_obj.limit == 10
    
    def test_filter_with_empty_data(self):
        """Test creating filter with empty data."""
        filter_obj = GetMultiPostsFilter()
        
        assert filter_obj.sort_field is None
        assert filter_obj.sort_order is None
        assert filter_obj.offset is None
        assert filter_obj.limit is None
    
    def test_filter_validation_valid_sort_order(self):
        """Test filter validation with valid sort order."""
        filter_obj = GetMultiPostsFilter(sort_order="ASC")
        filter_obj.validate_()  # Should not raise
        
        filter_obj = GetMultiPostsFilter(sort_order="DESC")
        filter_obj.validate_()  # Should not raise
    
    def test_filter_validation_invalid_sort_order(self):
        """Test filter validation with invalid sort order."""
        filter_obj = GetMultiPostsFilter(sort_order="INVALID")
        
        with pytest.raises(ValidationError, match="Invalid sort order"):
            filter_obj.validate_()
    
    def test_filter_validation_valid_dates(self):
        """Test filter validation with valid dates."""
        filter_obj = GetMultiPostsFilter(
            from_date="2023-01-01 00:00:00",
            to_date="2023-12-31 23:59:59"
        )
        filter_obj.validate_()  # Should not raise
    
    def test_filter_validation_invalid_from_date(self):
        """Test filter validation with invalid from_date."""
        filter_obj = GetMultiPostsFilter(from_date="invalid-date")
        
        with pytest.raises(ValidationError):
            filter_obj.validate_()
    
    def test_filter_validation_invalid_to_date(self):
        """Test filter validation with invalid to_date."""
        filter_obj = GetMultiPostsFilter(to_date="invalid-date")
        
        with pytest.raises(ValidationError):
            filter_obj.validate_()
    
    def test_filter_validation_valid_owner_id(self):
        """Test filter validation with valid owner_id."""
        filter_obj = GetMultiPostsFilter(owner_id=str(uuid.uuid4()))
        filter_obj.validate_()  # Should not raise
    
    def test_filter_validation_invalid_owner_id(self):
        """Test filter validation with invalid owner_id."""
        filter_obj = GetMultiPostsFilter(owner_id="invalid-uuid")
        
        with pytest.raises(ValidationError):
            filter_obj.validate_()


class TestCreatePostPayload:
    """Test cases for CreatePostPayload."""
    
    def test_create_payload_with_valid_data(self):
        """Test creating payload with valid data."""
        payload_data = {
            "id_": str(uuid.uuid4()),
            "text_content": "Test post content",
            "created_at": "2023-01-01T12:00:00.000000",
            "updated_at": "2023-01-01T12:30:00.000000",
            "owner_id": str(uuid.uuid4())
        }
        
        payload = CreatePostPayload(**payload_data)
        
        assert payload.id_ == payload_data["id_"]
        assert payload.text_content == payload_data["text_content"]
        assert payload.created_at == payload_data["created_at"]
        assert payload.owner_id == payload_data["owner_id"]
    
    def test_create_payload_with_empty_data(self):
        """Test creating payload with empty data."""
        payload = CreatePostPayload()
        
        assert payload.id_ is None
        assert payload.text_content is None
        assert payload.created_at is None
        assert payload.owner_id is None
    
    def test_create_payload_validation_valid_uuid(self):
        """Test payload validation with valid UUID."""
        payload = CreatePostPayload(id_=str(uuid.uuid4()))
        payload.validate_()  # Should not raise
    
    def test_create_payload_validation_invalid_uuid(self):
        """Test payload validation with invalid UUID."""
        payload = CreatePostPayload(id_="invalid-uuid")
        
        with pytest.raises(ValueError):
            payload.validate_()
    
    def test_create_payload_validation_valid_dates(self):
        """Test payload validation with valid dates."""
        payload = CreatePostPayload(
            created_at="2023-01-01T12:00:00.000000",
            updated_at="2023-01-01T12:30:00.000000"
        )
        payload.validate_()  # Should not raise
    
    def test_create_payload_validation_invalid_created_at(self):
        """Test payload validation with invalid created_at."""
        payload = CreatePostPayload(created_at="invalid-date")
        
        with pytest.raises(ValueError):
            payload.validate_()
    
    def test_create_payload_validation_invalid_updated_at(self):
        """Test payload validation with invalid updated_at."""
        payload = CreatePostPayload(updated_at="invalid-date")
        
        with pytest.raises(ValueError):
            payload.validate_()
    
    def test_create_payload_validation_valid_owner_id(self):
        """Test payload validation with valid owner_id."""
        payload = CreatePostPayload(owner_id=str(uuid.uuid4()))
        payload.validate_()  # Should not raise
    
    def test_create_payload_validation_invalid_owner_id(self):
        """Test payload validation with invalid owner_id."""
        payload = CreatePostPayload(owner_id="invalid-uuid")
        
        with pytest.raises(ValueError):
            payload.validate_()


class TestUpdatePostPayload:
    """Test cases for UpdatePostPayload."""
    
    def test_update_payload_with_valid_data(self):
        """Test creating update payload with valid data."""
        payload_data = {
            "id_": str(uuid.uuid4()),
            "text_content": "Updated post content",
            "updated_at": "2023-01-01T12:30:00.000000",
            "owner_id": str(uuid.uuid4())
        }
        
        payload = UpdatePostPayload(**payload_data)
        
        assert payload.id_ == payload_data["id_"]
        assert payload.text_content == payload_data["text_content"]
        assert payload.updated_at == payload_data["updated_at"]
        assert payload.owner_id == payload_data["owner_id"]
    
    def test_update_payload_validation_valid_uuid(self):
        """Test update payload validation with valid UUID."""
        payload = UpdatePostPayload(id_=str(uuid.uuid4()))
        payload.validate_()  # Should not raise
    
    def test_update_payload_validation_invalid_uuid(self):
        """Test update payload validation with invalid UUID."""
        payload = UpdatePostPayload(id_="invalid-uuid")
        
        with pytest.raises(ValueError):
            payload.validate_()
    
    def test_update_payload_validation_valid_updated_at(self):
        """Test update payload validation with valid updated_at."""
        payload = UpdatePostPayload(updated_at="2023-01-01 12:30:00")
        payload.validate_()  # Should not raise
    
    def test_update_payload_validation_invalid_updated_at(self):
        """Test update payload validation with invalid updated_at."""
        payload = UpdatePostPayload(updated_at="invalid-date")
        
        with pytest.raises(ValueError):
            payload.validate_()


class TestDeletePostPayload:
    """Test cases for DeletePostPayload."""
    
    def test_delete_payload_with_valid_data(self):
        """Test creating delete payload with valid data."""
        payload_data = {
            "id_": str(uuid.uuid4()),
            "owner_id": str(uuid.uuid4())
        }
        
        payload = DeletePostPayload(**payload_data)
        
        assert payload.id_ == payload_data["id_"]
        assert payload.owner_id == payload_data["owner_id"]
    
    def test_delete_payload_validation_valid_uuid(self):
        """Test delete payload validation with valid UUID."""
        payload = DeletePostPayload(id_=str(uuid.uuid4()))
        payload.validate_()  # Should not raise
    
    def test_delete_payload_validation_invalid_uuid(self):
        """Test delete payload validation with invalid UUID."""
        payload = DeletePostPayload(id_="invalid-uuid")
        
        with pytest.raises(ValueError):
            payload.validate_()
    
    def test_delete_payload_validation_valid_owner_id(self):
        """Test delete payload validation with valid owner_id."""
        payload = DeletePostPayload(owner_id=str(uuid.uuid4()))
        payload.validate_()  # Should not raise
    
    def test_delete_payload_validation_invalid_owner_id(self):
        """Test delete payload validation with invalid owner_id."""
        payload = DeletePostPayload(owner_id="invalid-uuid")
        
        with pytest.raises(ValueError):
            payload.validate_()