"""
Unit tests for Comment domain entities.
Tests CommentEntity and all its associated payload classes.
"""
import uuid
from datetime import datetime, timezone
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from internal.domains.entities.comment import (
    CommentEntity,
    GetMultiCommentsFilter,
    CreateCommentPayload,
    UpdateCommentPayload,
    DeleteCommentPayload
)
from internal.domains.entities.post import PostEntity
from internal.domains.entities.user import UserEntity


class TestCommentEntity:
    """Test cases for CommentEntity."""
    
    def test_comment_entity_creation_with_valid_data(self, sample_comment_data):
        """Test creating CommentEntity with valid data."""
        comment = CommentEntity(**sample_comment_data)
        
        assert comment.id_ == sample_comment_data["id_"]
        assert comment.text_content == sample_comment_data["text_content"]
        assert comment.created_at == sample_comment_data["created_at"]
        assert comment.updated_at == sample_comment_data["updated_at"]
        assert comment.post_id == sample_comment_data["post_id"]
        assert comment.owner_id == sample_comment_data["owner_id"]
        assert comment.post is None
        assert comment.owner is None
    
    def test_comment_entity_creation_with_relationships(self, sample_comment_data, sample_post_data, sample_user_data):
        """Test creating CommentEntity with post and owner relationships."""
        post = PostEntity(**sample_post_data)
        owner = UserEntity(**sample_user_data)
        sample_comment_data["post"] = post
        sample_comment_data["owner"] = owner
        
        comment = CommentEntity(**sample_comment_data)
        
        assert comment.post == post
        assert comment.owner == owner
        assert comment.post.id_ == sample_post_data["id_"]
        assert comment.owner.id_ == sample_user_data["id_"]
    
    def test_comment_entity_to_dict(self, sample_comment_data):
        """Test CommentEntity to_dict method."""
        comment = CommentEntity(**sample_comment_data)
        comment_dict = comment.to_dict()
        
        assert isinstance(comment_dict, dict)
        assert comment_dict["id_"] == str(sample_comment_data["id_"])
        assert comment_dict["text_content"] == sample_comment_data["text_content"]
        assert comment_dict["post_id"] == str(sample_comment_data["post_id"])
        assert comment_dict["owner_id"] == str(sample_comment_data["owner_id"])
    
    def test_comment_entity_to_dict_exclude_none(self, sample_comment_data):
        """Test CommentEntity to_dict with exclude_none=True."""
        comment = CommentEntity(**sample_comment_data)
        comment_dict = comment.to_dict(exclude_none=True)
        
        assert "updated_at" not in comment_dict
        assert "post" not in comment_dict
        assert "owner" not in comment_dict
    
    def test_comment_entity_invalid_id(self, sample_comment_data):
        """Test CommentEntity with invalid UUID."""
        sample_comment_data["id_"] = "invalid-uuid"
        
        with pytest.raises(ValidationError):
            CommentEntity(**sample_comment_data)
    
    def test_comment_entity_invalid_post_id(self, sample_comment_data):
        """Test CommentEntity with invalid post_id UUID."""
        sample_comment_data["post_id"] = "invalid-uuid"
        
        with pytest.raises(ValidationError):
            CommentEntity(**sample_comment_data)
    
    def test_comment_entity_invalid_owner_id(self, sample_comment_data):
        """Test CommentEntity with invalid owner_id UUID."""
        sample_comment_data["owner_id"] = "invalid-uuid"
        
        with pytest.raises(ValidationError):
            CommentEntity(**sample_comment_data)
    
    def test_comment_entity_missing_required_fields(self):
        """Test CommentEntity with missing required fields."""
        with pytest.raises(ValidationError):
            CommentEntity()
        
        with pytest.raises(ValidationError):
            CommentEntity(id_=uuid.uuid4())
        
        with pytest.raises(ValidationError):
            CommentEntity(id_=uuid.uuid4(), text_content="Test")


class TestGetMultiCommentsFilter:
    """Test cases for GetMultiCommentsFilter."""
    
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
            "post_id": str(uuid.uuid4()),
            "owner_id": str(uuid.uuid4())
        }
        
        filter_obj = GetMultiCommentsFilter(**filter_data)
        
        assert filter_obj.sort_field == "created_at"
        assert filter_obj.sort_order == "DESC"
        assert filter_obj.offset == 0
        assert filter_obj.limit == 10
        assert filter_obj.post_id == filter_data["post_id"]
        assert filter_obj.owner_id == filter_data["owner_id"]
    
    def test_filter_with_empty_data(self):
        """Test creating filter with empty data."""
        filter_obj = GetMultiCommentsFilter()
        
        assert filter_obj.sort_field is None
        assert filter_obj.sort_order is None
        assert filter_obj.offset is None
        assert filter_obj.limit is None
        assert filter_obj.post_id is None
        assert filter_obj.owner_id is None
    
    def test_filter_validation_valid_sort_order(self):
        """Test filter validation with valid sort order."""
        filter_obj = GetMultiCommentsFilter(sort_order="ASC")
        filter_obj.validate_()  # Should not raise
        
        filter_obj = GetMultiCommentsFilter(sort_order="DESC")
        filter_obj.validate_()  # Should not raise
    
    def test_filter_validation_invalid_sort_order(self):
        """Test filter validation with invalid sort order."""
        filter_obj = GetMultiCommentsFilter(sort_order="INVALID")
        
        with pytest.raises(ValidationError, match="Invalid sort order"):
            filter_obj.validate_()
    
    def test_filter_validation_valid_dates(self):
        """Test filter validation with valid dates."""
        filter_obj = GetMultiCommentsFilter(
            from_date="2023-01-01 00:00:00",
            to_date="2023-12-31 23:59:59"
        )
        filter_obj.validate_()  # Should not raise
    
    def test_filter_validation_invalid_from_date(self):
        """Test filter validation with invalid from_date."""
        filter_obj = GetMultiCommentsFilter(from_date="invalid-date")
        
        with pytest.raises(ValidationError):
            filter_obj.validate_()
    
    def test_filter_validation_invalid_to_date(self):
        """Test filter validation with invalid to_date."""
        filter_obj = GetMultiCommentsFilter(to_date="invalid-date")
        
        with pytest.raises(ValidationError):
            filter_obj.validate_()
    
    def test_filter_validation_valid_post_id(self):
        """Test filter validation with valid post_id."""
        filter_obj = GetMultiCommentsFilter(post_id=str(uuid.uuid4()))
        filter_obj.validate_()  # Should not raise
    
    def test_filter_validation_invalid_post_id(self):
        """Test filter validation with invalid post_id."""
        filter_obj = GetMultiCommentsFilter(post_id="invalid-uuid")
        
        with pytest.raises(ValidationError):
            filter_obj.validate_()
    
    def test_filter_validation_valid_owner_id(self):
        """Test filter validation with valid owner_id."""
        filter_obj = GetMultiCommentsFilter(owner_id=str(uuid.uuid4()))
        filter_obj.validate_()  # Should not raise
    
    def test_filter_validation_invalid_owner_id(self):
        """Test filter validation with invalid owner_id."""
        filter_obj = GetMultiCommentsFilter(owner_id="invalid-uuid")
        
        with pytest.raises(ValidationError):
            filter_obj.validate_()


class TestCreateCommentPayload:
    """Test cases for CreateCommentPayload."""
    
    def test_create_payload_with_valid_data(self):
        """Test creating payload with valid data."""
        payload_data = {
            "id_": str(uuid.uuid4()),
            "text_content": "Test comment content",
            "created_at": "2023-01-01 12:00:00",
            "updated_at": "2023-01-01 12:30:00",
            "post_id": str(uuid.uuid4()),
            "owner_id": str(uuid.uuid4())
        }
        
        payload = CreateCommentPayload(**payload_data)
        
        assert payload.id_ == payload_data["id_"]
        assert payload.text_content == payload_data["text_content"]
        assert payload.created_at == payload_data["created_at"]
        assert payload.updated_at == payload_data["updated_at"]
        assert payload.post_id == payload_data["post_id"]
        assert payload.owner_id == payload_data["owner_id"]
    
    def test_create_payload_with_empty_data(self):
        """Test creating payload with empty data."""
        payload = CreateCommentPayload()
        
        assert payload.id_ is None
        assert payload.text_content is None
        assert payload.created_at is None
        assert payload.updated_at is None
        assert payload.post_id is None
        assert payload.owner_id is None
    
    def test_create_payload_validation_valid_uuid(self):
        """Test payload validation with valid UUID."""
        payload = CreateCommentPayload(id_=str(uuid.uuid4()))
        payload.validate_()  # Should not raise
    
    def test_create_payload_validation_invalid_uuid(self):
        """Test payload validation with invalid UUID."""
        payload = CreateCommentPayload(id_="invalid-uuid")
        
        with pytest.raises(ValidationError):
            payload.validate_()
    
    def test_create_payload_validation_valid_dates(self):
        """Test payload validation with valid dates."""
        payload = CreateCommentPayload(
            created_at="2023-01-01 12:00:00",
            updated_at="2023-01-01 12:30:00"
        )
        payload.validate_()  # Should not raise
    
    def test_create_payload_validation_invalid_created_at(self):
        """Test payload validation with invalid created_at."""
        payload = CreateCommentPayload(created_at="invalid-date")
        
        with pytest.raises(ValidationError):
            payload.validate_()
    
    def test_create_payload_validation_invalid_updated_at(self):
        """Test payload validation with invalid updated_at."""
        payload = CreateCommentPayload(updated_at="invalid-date")
        
        with pytest.raises(ValidationError):
            payload.validate_()
    
    def test_create_payload_validation_valid_post_id(self):
        """Test payload validation with valid post_id."""
        payload = CreateCommentPayload(post_id=str(uuid.uuid4()))
        payload.validate_()  # Should not raise
    
    def test_create_payload_validation_invalid_post_id(self):
        """Test payload validation with invalid post_id."""
        payload = CreateCommentPayload(post_id="invalid-uuid")
        
        with pytest.raises(ValidationError):
            payload.validate_()
    
    def test_create_payload_validation_valid_owner_id(self):
        """Test payload validation with valid owner_id."""
        payload = CreateCommentPayload(owner_id=str(uuid.uuid4()))
        payload.validate_()  # Should not raise
    
    def test_create_payload_validation_invalid_owner_id(self):
        """Test payload validation with invalid owner_id."""
        payload = CreateCommentPayload(owner_id="invalid-uuid")
        
        with pytest.raises(ValidationError):
            payload.validate_()


class TestUpdateCommentPayload:
    """Test cases for UpdateCommentPayload."""
    
    def test_update_payload_with_valid_data(self):
        """Test creating update payload with valid data."""
        payload_data = {
            "id_": str(uuid.uuid4()),
            "text_content": "Updated comment content",
            "updated_at": "2023-01-01 12:30:00",
            "owner_id": str(uuid.uuid4())
        }
        
        payload = UpdateCommentPayload(**payload_data)
        
        assert payload.id_ == payload_data["id_"]
        assert payload.text_content == payload_data["text_content"]
        assert payload.updated_at == payload_data["updated_at"]
        assert payload.owner_id == payload_data["owner_id"]
    
    def test_update_payload_with_empty_data(self):
        """Test creating update payload with empty data."""
        payload = UpdateCommentPayload()
        
        assert payload.id_ is None
        assert payload.text_content is None
        assert payload.updated_at is None
        assert payload.owner_id is None
    
    def test_update_payload_validation_valid_uuid(self):
        """Test update payload validation with valid UUID."""
        payload = UpdateCommentPayload(id_=str(uuid.uuid4()))
        payload.validate_()  # Should not raise
    
    def test_update_payload_validation_invalid_uuid(self):
        """Test update payload validation with invalid UUID."""
        payload = UpdateCommentPayload(id_="invalid-uuid")
        
        with pytest.raises(ValidationError):
            payload.validate_()
    
    def test_update_payload_validation_valid_updated_at(self):
        """Test update payload validation with valid updated_at."""
        payload = UpdateCommentPayload(updated_at="2023-01-01 12:30:00")
        payload.validate_()  # Should not raise
    
    def test_update_payload_validation_invalid_updated_at(self):
        """Test update payload validation with invalid updated_at."""
        payload = UpdateCommentPayload(updated_at="invalid-date")
        
        with pytest.raises(ValidationError):
            payload.validate_()
    
    def test_update_payload_validation_valid_owner_id(self):
        """Test update payload validation with valid owner_id."""
        payload = UpdateCommentPayload(owner_id=str(uuid.uuid4()))
        payload.validate_()  # Should not raise
    
    def test_update_payload_validation_invalid_owner_id(self):
        """Test update payload validation with invalid owner_id."""
        payload = UpdateCommentPayload(owner_id="invalid-uuid")
        
        with pytest.raises(ValidationError):
            payload.validate_()


class TestDeleteCommentPayload:
    """Test cases for DeleteCommentPayload."""
    
    def test_delete_payload_with_valid_data(self):
        """Test creating delete payload with valid data."""
        payload_data = {
            "id_": str(uuid.uuid4()),
            "owner_id": str(uuid.uuid4())
        }
        
        payload = DeleteCommentPayload(**payload_data)
        
        assert payload.id_ == payload_data["id_"]
        assert payload.owner_id == payload_data["owner_id"]
    
    def test_delete_payload_with_empty_data(self):
        """Test creating delete payload with empty data."""
        payload = DeleteCommentPayload()
        
        assert payload.id_ is None
        assert payload.owner_id is None
    
    def test_delete_payload_validation_valid_uuid(self):
        """Test delete payload validation with valid UUID."""
        payload = DeleteCommentPayload(id_=str(uuid.uuid4()))
        payload.validate_()  # Should not raise
    
    def test_delete_payload_validation_invalid_uuid(self):
        """Test delete payload validation with invalid UUID."""
        payload = DeleteCommentPayload(id_="invalid-uuid")
        
        with pytest.raises(ValidationError):
            payload.validate_()
    
    def test_delete_payload_validation_valid_owner_id(self):
        """Test delete payload validation with valid owner_id."""
        payload = DeleteCommentPayload(owner_id=str(uuid.uuid4()))
        payload.validate_()  # Should not raise
    
    def test_delete_payload_validation_invalid_owner_id(self):
        """Test delete payload validation with invalid owner_id."""
        payload = DeleteCommentPayload(owner_id="invalid-uuid")
        
        with pytest.raises(ValidationError):
            payload.validate_()


class TestCommentEntityEdgeCases:
    """Test edge cases and boundary conditions for CommentEntity."""
    
    def test_comment_with_very_long_text_content(self, sample_comment_data):
        """Test CommentEntity with very long text content."""
        long_content = "x" * 10000  # Very long text
        sample_comment_data["text_content"] = long_content
        
        comment = CommentEntity(**sample_comment_data)
        assert comment.text_content == long_content
    
    def test_comment_with_empty_text_content(self, sample_comment_data):
        """Test CommentEntity with empty text content."""
        sample_comment_data["text_content"] = ""
        
        comment = CommentEntity(**sample_comment_data)
        assert comment.text_content == ""
    
    def test_comment_with_whitespace_only_text_content(self, sample_comment_data):
        """Test CommentEntity with whitespace-only text content."""
        sample_comment_data["text_content"] = "   \n\t  "
        
        comment = CommentEntity(**sample_comment_data)
        assert comment.text_content == "   \n\t  "
    
    def test_comment_with_special_characters(self, sample_comment_data):
        """Test CommentEntity with special characters in text content."""
        special_content = "Test with special chars: !@#$%^&*()_+{}|:<>?[]\\;'\",./"
        sample_comment_data["text_content"] = special_content
        
        comment = CommentEntity(**sample_comment_data)
        assert comment.text_content == special_content
    
    def test_comment_with_unicode_characters(self, sample_comment_data):
        """Test CommentEntity with unicode characters."""
        unicode_content = "Test with unicode: 你好 🌟 🎉 ñáéíóú"
        sample_comment_data["text_content"] = unicode_content
        
        comment = CommentEntity(**sample_comment_data)
        assert comment.text_content == unicode_content