"""
Unit tests for Authorization domain entities.
Tests permission entities and authorization-related payload validation.
"""
import uuid
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from internal.domains.entities.authorization import (
    PermEntity,
    CreateSinglePermPayload
)
from internal.domains.constants.v1_authorization import V1ReBACRelation, V1ReBACObjectType


class TestPermEntity:
    """Test cases for PermEntity."""
    
    def test_perm_entity_creation_with_valid_data(self):
        """Test creating PermEntity with valid data."""
        perm_data = {
            "target_obj": "post:123e4567-e89b-12d3-a456-426614174000",
            "relation": "can_view",
            "request_obj": "user:987fcdeb-51a2-43d1-b456-426614174111"
        }
        
        perm = PermEntity(**perm_data)
        
        assert perm.target_obj == perm_data["target_obj"]
        assert perm.relation == perm_data["relation"]
        assert perm.request_obj == perm_data["request_obj"]
    
    def test_perm_entity_creation_with_different_object_types(self):
        """Test creating PermEntity with different object types."""
        # Test with user target and post request
        perm1 = PermEntity(
            target_obj="user:123e4567-e89b-12d3-a456-426614174000",
            relation="is_owner",
            request_obj="post:987fcdeb-51a2-43d1-b456-426614174111"
        )
        
        assert "user:" in perm1.target_obj
        assert "post:" in perm1.request_obj
        
        # Test with comment target and user request
        perm2 = PermEntity(
            target_obj="comment:aaa1111-bbbb-cccc-dddd-eeeeeeeeeeee",
            relation="can_edit",
            request_obj="user:fff2222-gggg-hhhh-iiii-jjjjjjjjjjjj"
        )
        
        assert "comment:" in perm2.target_obj
        assert "user:" in perm2.request_obj
    
    def test_perm_entity_creation_with_various_relations(self):
        """Test creating PermEntity with various relation types."""
        relations = [
            "is_super_admin",
            "is_owner", 
            "can_create",
            "can_get_detail",
            "can_get_list",
            "can_update",
            "can_delete"
        ]
        
        for relation in relations:
            perm = PermEntity(
                target_obj="post:123e4567-e89b-12d3-a456-426614174000",
                relation=relation,
                request_obj="user:987fcdeb-51a2-43d1-b456-426614174111"
            )
            assert perm.relation == relation
    
    def test_perm_entity_missing_required_fields(self):
        """Test PermEntity with missing required fields."""
        with pytest.raises(ValidationError):
            PermEntity()
        
        with pytest.raises(ValidationError):
            PermEntity(target_obj="post:123")
        
        with pytest.raises(ValidationError):
            PermEntity(target_obj="post:123", relation="can_view")
    
    def test_perm_entity_with_empty_strings(self):
        """Test PermEntity with empty string fields."""
        # Empty strings should be allowed by Pydantic validation
        # but might be caught by custom validation in payloads
        perm = PermEntity(
            target_obj="",
            relation="",
            request_obj=""
        )
        
        assert perm.target_obj == ""
        assert perm.relation == ""
        assert perm.request_obj == ""
    
    def test_perm_entity_with_complex_object_identifiers(self):
        """Test PermEntity with complex object identifiers."""
        # Test with multiple colons in identifiers
        perm = PermEntity(
            target_obj="namespace:post:123e4567-e89b-12d3-a456-426614174000",
            relation="can_view",
            request_obj="tenant:user:987fcdeb-51a2-43d1-b456-426614174111"
        )
        
        assert "namespace:post:" in perm.target_obj
        assert "tenant:user:" in perm.request_obj


class TestCreateSinglePermPayload:
    """Test cases for CreateSinglePermPayload."""
    
    def test_create_perm_payload_with_valid_data(self):
        """Test creating CreateSinglePermPayload with valid data."""
        payload_data = {
            "target_obj": "post:123e4567-e89b-12d3-a456-426614174000",
            "relation": V1ReBACRelation.CAN_GET_DETAIL,
            "request_obj": "user:987fcdeb-51a2-43d1-b456-426614174111"
        }
        
        payload = CreateSinglePermPayload(**payload_data)
        
        assert payload.target_obj == payload_data["target_obj"]
        assert payload.relation == V1ReBACRelation.CAN_GET_DETAIL
        assert payload.request_obj == payload_data["request_obj"]
    
    def test_create_perm_payload_with_all_relations(self):
        """Test CreateSinglePermPayload with all possible relations."""
        for relation in V1ReBACRelation:
            payload = CreateSinglePermPayload(
                target_obj="post:123e4567-e89b-12d3-a456-426614174000",
                relation=relation,
                request_obj="user:987fcdeb-51a2-43d1-b456-426614174111"
            )
            assert payload.relation == relation
    
    def test_create_perm_payload_validation_valid_objects(self):
        """Test CreateSinglePermPayload validation with valid objects."""
        payload = CreateSinglePermPayload(
            target_obj="post:123e4567-e89b-12d3-a456-426614174000",
            relation=V1ReBACRelation.CAN_UPDATE,
            request_obj="user:987fcdeb-51a2-43d1-b456-426614174111"
        )
        
        # Should not raise any exception
        payload.validate_()
    
    def test_create_perm_payload_validation_empty_target_obj(self):
        """Test CreateSinglePermPayload validation with empty target_obj."""
        payload = CreateSinglePermPayload(
            target_obj="",
            relation=V1ReBACRelation.CAN_VIEW,
            request_obj="user:987fcdeb-51a2-43d1-b456-426614174111"
        )
        
        with pytest.raises(ValidationError, match="Empty target_obj"):
            payload.validate_()
    
    def test_create_perm_payload_validation_invalid_target_obj_format(self):
        """Test CreateSinglePermPayload validation with invalid target_obj format."""
        payload = CreateSinglePermPayload(
            target_obj="invalidformat",  # Missing colon separator
            relation=V1ReBACRelation.CAN_VIEW,
            request_obj="user:987fcdeb-51a2-43d1-b456-426614174111"
        )
        
        with pytest.raises(ValidationError, match="target_obj must follow pattern: <object_type:id>"):
            payload.validate_()
    
    def test_create_perm_payload_validation_empty_request_obj(self):
        """Test CreateSinglePermPayload validation with empty request_obj."""
        payload = CreateSinglePermPayload(
            target_obj="post:123e4567-e89b-12d3-a456-426614174000",
            relation=V1ReBACRelation.CAN_VIEW,
            request_obj=""
        )
        
        with pytest.raises(ValidationError, match="Empty request_obj"):
            payload.validate_()
    
    def test_create_perm_payload_validation_invalid_request_obj_format(self):
        """Test CreateSinglePermPayload validation with invalid request_obj format."""
        payload = CreateSinglePermPayload(
            target_obj="post:123e4567-e89b-12d3-a456-426614174000",
            relation=V1ReBACRelation.CAN_VIEW,
            request_obj="invalidformat"  # Missing colon separator
        )
        
        with pytest.raises(ValidationError, match="request_obj must follow pattern: <object_type:id>"):
            payload.validate_()
    
    def test_create_perm_payload_validation_with_valid_formats(self):
        """Test CreateSinglePermPayload validation with various valid formats."""
        valid_formats = [
            ("post:123", "user:456"),
            ("user:uuid-here", "post:another-uuid"),
            ("comment:short-id", "user:long-uuid-identifier"),
            ("post:123e4567-e89b-12d3-a456-426614174000", "user:987fcdeb-51a2-43d1-b456-426614174111"),
            ("user:admin", "post:public"),
            ("comment:1", "user:superadmin")
        ]
        
        for target_obj, request_obj in valid_formats:
            payload = CreateSinglePermPayload(
                target_obj=target_obj,
                relation=V1ReBACRelation.CAN_VIEW,
                request_obj=request_obj
            )
            # Should not raise any exception
            payload.validate_()
    
    def test_create_perm_payload_validation_with_multiple_colons(self):
        """Test CreateSinglePermPayload validation with objects containing multiple colons."""
        payload = CreateSinglePermPayload(
            target_obj="namespace:post:123e4567-e89b-12d3-a456-426614174000",
            relation=V1ReBACRelation.CAN_VIEW,
            request_obj="tenant:user:987fcdeb-51a2-43d1-b456-426614174111"
        )
        
        # Should not raise any exception - multiple colons should be allowed
        payload.validate_()
    
    def test_create_perm_payload_validation_edge_cases(self):
        """Test CreateSinglePermPayload validation with edge cases."""
        # Test with minimal valid format
        payload1 = CreateSinglePermPayload(
            target_obj="a:b",
            relation=V1ReBACRelation.CAN_VIEW,
            request_obj="c:d"
        )
        payload1.validate_()  # Should not raise
        
        # Test with very long identifiers
        long_id = "x" * 1000
        payload2 = CreateSinglePermPayload(
            target_obj=f"post:{long_id}",
            relation=V1ReBACRelation.CAN_VIEW,
            request_obj=f"user:{long_id}"
        )
        payload2.validate_()  # Should not raise
    
    def test_create_perm_payload_missing_required_fields(self):
        """Test CreateSinglePermPayload with missing required fields."""
        with pytest.raises(ValidationError):
            CreateSinglePermPayload()
        
        with pytest.raises(ValidationError):
            CreateSinglePermPayload(target_obj="post:123")
        
        with pytest.raises(ValidationError):
            CreateSinglePermPayload(
                target_obj="post:123",
                relation=V1ReBACRelation.CAN_VIEW
            )


class TestAuthorizationEntityEdgeCases:
    """Test edge cases and boundary conditions for authorization entities."""
    
    def test_perm_entity_with_special_characters(self):
        """Test PermEntity with special characters in identifiers."""
        special_chars_data = {
            "target_obj": "post:123e4567-e89b-12d3-a456-426614174000@special",
            "relation": "can_view#permission",
            "request_obj": "user:987fcdeb-51a2-43d1-b456-426614174111!@#$%"
        }
        
        perm = PermEntity(**special_chars_data)
        
        assert "@special" in perm.target_obj
        assert "#permission" in perm.relation
        assert "!@#$%" in perm.request_obj
    
    def test_perm_entity_with_unicode_characters(self):
        """Test PermEntity with unicode characters."""
        unicode_data = {
            "target_obj": "post:用户123",
            "relation": "can_view_权限",
            "request_obj": "user:用户987"
        }
        
        perm = PermEntity(**unicode_data)
        
        assert "用户123" in perm.target_obj
        assert "权限" in perm.relation
        assert "用户987" in perm.request_obj
    
    def test_create_perm_payload_with_realistic_uuids(self):
        """Test CreateSinglePermPayload with realistic UUID formats."""
        realistic_payloads = [
            {
                "target_obj": f"post:{uuid.uuid4()}",
                "relation": V1ReBACRelation.IS_OWNER,
                "request_obj": f"user:{uuid.uuid4()}"
            },
            {
                "target_obj": f"comment:{uuid.uuid4()}",
                "relation": V1ReBACRelation.CAN_DELETE,
                "request_obj": f"user:{uuid.uuid4()}"
            },
            {
                "target_obj": f"user:{uuid.uuid4()}",
                "relation": V1ReBACRelation.IS_SUPER_ADMIN,
                "request_obj": f"user:{uuid.uuid4()}"
            }
        ]
        
        for payload_data in realistic_payloads:
            payload = CreateSinglePermPayload(**payload_data)
            payload.validate_()  # Should not raise
            
            assert ":" in payload.target_obj
            assert ":" in payload.request_obj
            assert payload.relation in V1ReBACRelation
    
    def test_create_perm_payload_validation_boundary_conditions(self):
        """Test CreateSinglePermPayload validation boundary conditions."""
        # Test with single character after colon
        payload1 = CreateSinglePermPayload(
            target_obj="post:1",
            relation=V1ReBACRelation.CAN_VIEW,
            request_obj="user:2"
        )
        payload1.validate_()  # Should not raise
        
        # Test with empty string after colon (should still be valid as it has colon)
        payload2 = CreateSinglePermPayload(
            target_obj="post:",
            relation=V1ReBACRelation.CAN_VIEW,
            request_obj="user:"
        )
        payload2.validate_()  # Should not raise
        
        # Test with multiple consecutive colons
        payload3 = CreateSinglePermPayload(
            target_obj="post::123",
            relation=V1ReBACRelation.CAN_VIEW,
            request_obj="user::456"
        )
        payload3.validate_()  # Should not raise
    
    def test_create_perm_payload_with_object_type_combinations(self):
        """Test CreateSinglePermPayload with different object type combinations."""
        object_types = ["user", "post", "comment"]
        
        for target_type in object_types:
            for request_type in object_types:
                payload = CreateSinglePermPayload(
                    target_obj=f"{target_type}:{uuid.uuid4()}",
                    relation=V1ReBACRelation.CAN_VIEW,
                    request_obj=f"{request_type}:{uuid.uuid4()}"
                )
                payload.validate_()  # Should not raise
                
                assert payload.target_obj.startswith(target_type)
                assert payload.request_obj.startswith(request_type)
    
    def test_perm_entity_serialization_deserialization(self):
        """Test PermEntity serialization and deserialization."""
        original_data = {
            "target_obj": "post:123e4567-e89b-12d3-a456-426614174000",
            "relation": "can_view",
            "request_obj": "user:987fcdeb-51a2-43d1-b456-426614174111"
        }
        
        perm = PermEntity(**original_data)
        
        # Test model_dump
        serialized = perm.model_dump()
        assert serialized == original_data
        
        # Test recreation from serialized data
        perm_recreated = PermEntity(**serialized)
        assert perm_recreated.target_obj == perm.target_obj
        assert perm_recreated.relation == perm.relation
        assert perm_recreated.request_obj == perm.request_obj
    
    def test_create_perm_payload_with_whitespace_handling(self):
        """Test CreateSinglePermPayload with whitespace in object identifiers."""
        # Test with spaces (should be preserved)
        payload = CreateSinglePermPayload(
            target_obj="post: spaced id ",
            relation=V1ReBACRelation.CAN_VIEW,
            request_obj="user: another spaced id "
        )
        
        assert " spaced id " in payload.target_obj
        assert " another spaced id " in payload.request_obj
        
        # Validation should still pass as long as colon is present
        payload.validate_()  # Should not raise