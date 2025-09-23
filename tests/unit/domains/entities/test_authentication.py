"""
Unit tests for Authentication domain entities.
Tests JWT payload, webhook events, and all authentication-related entities.
"""
import uuid
from datetime import datetime, timezone
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from internal.domains.entities.authentication import (
    RealmAccess,
    ResourceAccessRoles,
    ResourceAccess,
    JWTPayload,
    WebhookEventActionByEntity,
    WebhookEventResourceUserDetails,
    WebhookEventEntity
)
from internal.domains.constants.authentication import WebhookEventOperation, WebhookEventResource


class TestRealmAccess:
    """Test cases for RealmAccess."""
    
    def test_realm_access_creation_with_roles(self):
        """Test creating RealmAccess with roles."""
        roles = ["admin", "user", "manager"]
        realm_access = RealmAccess(roles=roles)
        
        assert realm_access.roles == roles
    
    def test_realm_access_creation_without_roles(self):
        """Test creating RealmAccess without roles."""
        realm_access = RealmAccess()
        
        assert realm_access.roles is None
    
    def test_realm_access_creation_with_empty_roles(self):
        """Test creating RealmAccess with empty roles list."""
        realm_access = RealmAccess(roles=[])
        
        assert realm_access.roles == []
    
    def test_realm_access_creation_with_single_role(self):
        """Test creating RealmAccess with single role."""
        realm_access = RealmAccess(roles=["admin"])
        
        assert realm_access.roles == ["admin"]


class TestResourceAccessRoles:
    """Test cases for ResourceAccessRoles."""
    
    def test_resource_access_roles_creation_with_roles(self):
        """Test creating ResourceAccessRoles with roles."""
        roles = ["view", "edit", "delete"]
        resource_roles = ResourceAccessRoles(roles=roles)
        
        assert resource_roles.roles == roles
    
    def test_resource_access_roles_creation_without_roles(self):
        """Test creating ResourceAccessRoles without roles."""
        resource_roles = ResourceAccessRoles()
        
        assert resource_roles.roles is None


class TestResourceAccess:
    """Test cases for ResourceAccess."""
    
    def test_resource_access_creation_with_account(self):
        """Test creating ResourceAccess with account."""
        account_roles = ResourceAccessRoles(roles=["view", "edit"])
        resource_access = ResourceAccess(account=account_roles)
        
        assert resource_access.account == account_roles
        assert resource_access.account.roles == ["view", "edit"]
    
    def test_resource_access_creation_without_account(self):
        """Test creating ResourceAccess without account."""
        resource_access = ResourceAccess()
        
        assert resource_access.account is None


class TestJWTPayload:
    """Test cases for JWTPayload."""
    
    def test_jwt_payload_creation_with_all_fields(self):
        """Test creating JWTPayload with all fields."""
        realm_access = RealmAccess(roles=["admin", "user"])
        resource_access = ResourceAccess(account=ResourceAccessRoles(roles=["view"]))
        
        jwt_data = {
            "exp": 1672531200,  # 2023-01-01 00:00:00 UTC
            "iat": 1672444800,  # 2022-12-31 00:00:00 UTC
            "jti": str(uuid.uuid4()),
            "iss": "https://keycloak.example.com",
            "aud": "test-client",
            "sub": str(uuid.uuid4()),
            "typ": "Bearer",
            "azp": "test-client",
            "sid": str(uuid.uuid4()),
            "acr": "1",
            "allowed_origins": ["https://example.com"],
            "realm_access": realm_access,
            "resource_access": resource_access,
            "scope": "openid email profile",
            "email_verified": True,
            "name": "John Doe",
            "preferred_username": "johndoe",
            "given_name": "John",
            "family_name": "Doe",
            "email": "john.doe@example.com"
        }
        
        jwt_payload = JWTPayload(**jwt_data)
        
        assert jwt_payload.exp == jwt_data["exp"]
        assert jwt_payload.iat == jwt_data["iat"]
        assert jwt_payload.jti == jwt_data["jti"]
        assert jwt_payload.iss == jwt_data["iss"]
        assert jwt_payload.aud == jwt_data["aud"]
        assert jwt_payload.sub == jwt_data["sub"]
        assert jwt_payload.typ == jwt_data["typ"]
        assert jwt_payload.azp == jwt_data["azp"]
        assert jwt_payload.sid == jwt_data["sid"]
        assert jwt_payload.acr == jwt_data["acr"]
        assert jwt_payload.allowed_origins == jwt_data["allowed_origins"]
        assert jwt_payload.realm_access == realm_access
        assert jwt_payload.resource_access == resource_access
        assert jwt_payload.scope == jwt_data["scope"]
        assert jwt_payload.email_verified == jwt_data["email_verified"]
        assert jwt_payload.name == jwt_data["name"]
        assert jwt_payload.preferred_username == jwt_data["preferred_username"]
        assert jwt_payload.given_name == jwt_data["given_name"]
        assert jwt_payload.family_name == jwt_data["family_name"]
        assert jwt_payload.email == jwt_data["email"]
    
    def test_jwt_payload_creation_with_minimal_fields(self):
        """Test creating JWTPayload with minimal fields."""
        jwt_payload = JWTPayload()
        
        assert jwt_payload.exp is None
        assert jwt_payload.iat is None
        assert jwt_payload.jti is None
        assert jwt_payload.realm_access is None
        assert jwt_payload.email_verified is None
    
    def test_jwt_payload_get_exp_datetime_valid(self):
        """Test JWTPayload get_exp_datetime with valid timestamp."""
        exp_timestamp = 1672531200  # 2023-01-01 00:00:00 UTC
        jwt_payload = JWTPayload(exp=exp_timestamp)
        
        exp_datetime = jwt_payload.get_exp_datetime()
        
        assert exp_datetime is not None
        assert exp_datetime.year == 2023
        assert exp_datetime.month == 1
        assert exp_datetime.day == 1
    
    def test_jwt_payload_get_exp_datetime_none(self):
        """Test JWTPayload get_exp_datetime with None timestamp."""
        jwt_payload = JWTPayload(exp=None)
        
        exp_datetime = jwt_payload.get_exp_datetime()
        
        assert exp_datetime is None
    
    def test_jwt_payload_get_iat_datetime_valid(self):
        """Test JWTPayload get_iat_datetime with valid timestamp."""
        iat_timestamp = 1672444800  # 2022-12-31 00:00:00 UTC
        jwt_payload = JWTPayload(iat=iat_timestamp)
        
        iat_datetime = jwt_payload.get_iat_datetime()
        
        assert iat_datetime is not None
        assert iat_datetime.year == 2022
        assert iat_datetime.month == 12
        assert iat_datetime.day == 31
    
    def test_jwt_payload_get_iat_datetime_none(self):
        """Test JWTPayload get_iat_datetime with None timestamp."""
        jwt_payload = JWTPayload(iat=None)
        
        iat_datetime = jwt_payload.get_iat_datetime()
        
        assert iat_datetime is None
    
    def test_jwt_payload_with_nested_structures(self):
        """Test JWTPayload with nested realm and resource access."""
        jwt_data = {
            "realm_access": {"roles": ["admin", "user"]},
            "resource_access": {"account": {"roles": ["manage-account", "view-profile"]}}
        }
        
        jwt_payload = JWTPayload(**jwt_data)
        
        assert isinstance(jwt_payload.realm_access, RealmAccess)
        assert jwt_payload.realm_access.roles == ["admin", "user"]
        assert isinstance(jwt_payload.resource_access, ResourceAccess)
        assert isinstance(jwt_payload.resource_access.account, ResourceAccessRoles)
        assert jwt_payload.resource_access.account.roles == ["manage-account", "view-profile"]


class TestWebhookEventActionByEntity:
    """Test cases for WebhookEventActionByEntity."""
    
    def test_webhook_action_by_creation_with_all_fields(self):
        """Test creating WebhookEventActionByEntity with all fields."""
        action_data = {
            "id_": str(uuid.uuid4()),
            "username": "admin_user",
            "realm_id": "test-realm",
            "client_id": "admin-cli",
            "ip_address": "192.168.1.100"
        }
        
        action_by = WebhookEventActionByEntity(**action_data)
        
        assert action_by.id_ == action_data["id_"]
        assert action_by.username == action_data["username"]
        assert action_by.realm_id == action_data["realm_id"]
        assert action_by.client_id == action_data["client_id"]
        assert action_by.ip_address == action_data["ip_address"]
    
    def test_webhook_action_by_creation_without_ip(self):
        """Test creating WebhookEventActionByEntity without IP address."""
        action_data = {
            "id_": str(uuid.uuid4()),
            "username": "admin_user",
            "realm_id": "test-realm",
            "client_id": "admin-cli"
        }
        
        action_by = WebhookEventActionByEntity(**action_data)
        
        assert action_by.ip_address is None
    
    def test_webhook_action_by_missing_required_fields(self):
        """Test WebhookEventActionByEntity with missing required fields."""
        with pytest.raises(ValidationError):
            WebhookEventActionByEntity()
        
        with pytest.raises(ValidationError):
            WebhookEventActionByEntity(id_=str(uuid.uuid4()))


class TestWebhookEventResourceUserDetails:
    """Test cases for WebhookEventResourceUserDetails."""
    
    def test_webhook_user_details_creation_with_all_fields(self):
        """Test creating WebhookEventResourceUserDetails with all fields."""
        user_data = {
            "id_": str(uuid.uuid4()),
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "email": "testuser@example.com",
            "created_at": datetime.now(timezone.utc),
            "is_active": True
        }
        
        user_details = WebhookEventResourceUserDetails(**user_data)
        
        assert user_details.id_ == user_data["id_"]
        assert user_details.username == user_data["username"]
        assert user_details.first_name == user_data["first_name"]
        assert user_details.last_name == user_data["last_name"]
        assert user_details.email == user_data["email"]
        assert user_details.created_at == user_data["created_at"]
        assert user_details.is_active == user_data["is_active"]
    
    def test_webhook_user_details_creation_with_minimal_fields(self):
        """Test creating WebhookEventResourceUserDetails with minimal fields."""
        user_details = WebhookEventResourceUserDetails()
        
        assert user_details.id_ is None
        assert user_details.username is None
        assert user_details.first_name is None
        assert user_details.last_name is None
        assert user_details.email is None
        assert user_details.created_at is None
        assert user_details.is_active is None
    
    def test_webhook_user_details_with_partial_data(self):
        """Test creating WebhookEventResourceUserDetails with partial data."""
        user_details = WebhookEventResourceUserDetails(
            username="testuser",
            email="testuser@example.com",
            is_active=True
        )
        
        assert user_details.username == "testuser"
        assert user_details.email == "testuser@example.com"
        assert user_details.is_active is True
        assert user_details.id_ is None
        assert user_details.first_name is None


class TestWebhookEventEntity:
    """Test cases for WebhookEventEntity."""
    
    def test_webhook_event_creation_with_valid_data(self):
        """Test creating WebhookEventEntity with valid data."""
        action_by = WebhookEventActionByEntity(
            id_=str(uuid.uuid4()),
            username="admin_user",
            realm_id="test-realm",
            client_id="admin-cli",
            ip_address="192.168.1.100"
        )
        
        user_details = WebhookEventResourceUserDetails(
            id_=str(uuid.uuid4()),
            username="testuser",
            email="testuser@example.com",
            is_active=True
        )
        
        event_data = {
            "realm_name": "test-realm",
            "operation": WebhookEventOperation.CREATE,
            "action_by": action_by,
            "action_at": datetime.now(timezone.utc),
            "resource": WebhookEventResource.USER,
            "resource_detail": user_details
        }
        
        webhook_event = WebhookEventEntity(**event_data)
        
        assert webhook_event.realm_name == event_data["realm_name"]
        assert webhook_event.operation == WebhookEventOperation.CREATE
        assert webhook_event.action_by == action_by
        assert webhook_event.action_at == event_data["action_at"]
        assert webhook_event.resource == WebhookEventResource.USER
        assert webhook_event.resource_detail == user_details
    
    def test_webhook_event_with_different_operations(self):
        """Test WebhookEventEntity with different operation types."""
        action_by = WebhookEventActionByEntity(
            id_=str(uuid.uuid4()),
            username="admin_user",
            realm_id="test-realm",
            client_id="admin-cli"
        )
        
        user_details = WebhookEventResourceUserDetails(username="testuser")
        
        for operation in [WebhookEventOperation.CREATE, WebhookEventOperation.UPDATE, WebhookEventOperation.DELETE]:
            event_data = {
                "realm_name": "test-realm",
                "operation": operation,
                "action_by": action_by,
                "action_at": datetime.now(timezone.utc),
                "resource": WebhookEventResource.USER,
                "resource_detail": user_details
            }
            
            webhook_event = WebhookEventEntity(**event_data)
            assert webhook_event.operation == operation
    
    def test_webhook_event_missing_required_fields(self):
        """Test WebhookEventEntity with missing required fields."""
        with pytest.raises(ValidationError):
            WebhookEventEntity()
        
        with pytest.raises(ValidationError):
            WebhookEventEntity(realm_name="test-realm")
    
    def test_webhook_event_with_nested_dict_data(self):
        """Test WebhookEventEntity creation with nested dictionary data."""
        event_data = {
            "realm_name": "test-realm",
            "operation": WebhookEventOperation.UPDATE,
            "action_by": {
                "id_": str(uuid.uuid4()),
                "username": "admin_user",
                "realm_id": "test-realm",
                "client_id": "admin-cli",
                "ip_address": "10.0.0.1"
            },
            "action_at": datetime.now(timezone.utc),
            "resource": WebhookEventResource.USER,
            "resource_detail": {
                "id_": str(uuid.uuid4()),
                "username": "updated_user",
                "first_name": "Updated",
                "last_name": "User",
                "email": "updated@example.com",
                "is_active": False
            }
        }
        
        webhook_event = WebhookEventEntity(**event_data)
        
        assert isinstance(webhook_event.action_by, WebhookEventActionByEntity)
        assert webhook_event.action_by.username == "admin_user"
        assert webhook_event.action_by.ip_address == "10.0.0.1"
        
        assert isinstance(webhook_event.resource_detail, WebhookEventResourceUserDetails)
        assert webhook_event.resource_detail.username == "updated_user"
        assert webhook_event.resource_detail.is_active is False


class TestAuthenticationEntityEdgeCases:
    """Test edge cases and boundary conditions for authentication entities."""
    
    def test_jwt_payload_with_invalid_timestamps(self):
        """Test JWTPayload with invalid timestamps."""
        # Very old timestamp
        jwt_payload = JWTPayload(exp=0, iat=0)
        
        exp_datetime = jwt_payload.get_exp_datetime()
        iat_datetime = jwt_payload.get_iat_datetime()
        
        assert exp_datetime.year == 1970
        assert iat_datetime.year == 1970
    
    def test_jwt_payload_with_future_timestamps(self):
        """Test JWTPayload with future timestamps."""
        # Far future timestamp
        future_timestamp = 4102444800  # 2100-01-01
        jwt_payload = JWTPayload(exp=future_timestamp, iat=future_timestamp)
        
        exp_datetime = jwt_payload.get_exp_datetime()
        iat_datetime = jwt_payload.get_iat_datetime()
        
        assert exp_datetime.year == 2100
        assert iat_datetime.year == 2100
    
    def test_jwt_payload_with_empty_lists_and_strings(self):
        """Test JWTPayload with empty lists and strings."""
        jwt_payload = JWTPayload(
            allowed_origins=[],
            scope="",
            name="",
            email="",
            realm_access=RealmAccess(roles=[])
        )
        
        assert jwt_payload.allowed_origins == []
        assert jwt_payload.scope == ""
        assert jwt_payload.name == ""
        assert jwt_payload.email == ""
        assert jwt_payload.realm_access.roles == []
    
    def test_webhook_event_with_very_long_strings(self):
        """Test WebhookEventEntity with very long string values."""
        long_realm_name = "x" * 1000
        long_username = "y" * 500
        
        action_by = WebhookEventActionByEntity(
            id_=str(uuid.uuid4()),
            username=long_username,
            realm_id="test-realm",
            client_id="admin-cli"
        )
        
        user_details = WebhookEventResourceUserDetails(username=long_username)
        
        webhook_event = WebhookEventEntity(
            realm_name=long_realm_name,
            operation=WebhookEventOperation.CREATE,
            action_by=action_by,
            action_at=datetime.now(timezone.utc),
            resource=WebhookEventResource.USER,
            resource_detail=user_details
        )
        
        assert webhook_event.realm_name == long_realm_name
        assert webhook_event.action_by.username == long_username
    
    def test_webhook_event_with_special_characters(self):
        """Test WebhookEventEntity with special characters."""
        special_realm = "test-realm!@#$%^&*()"
        special_username = "user@domain.com-123_test"
        
        action_by = WebhookEventActionByEntity(
            id_=str(uuid.uuid4()),
            username=special_username,
            realm_id=special_realm,
            client_id="client-123"
        )
        
        user_details = WebhookEventResourceUserDetails(
            username=special_username,
            email="user+tag@example.co.uk",
            first_name="José",
            last_name="García-López"
        )
        
        webhook_event = WebhookEventEntity(
            realm_name=special_realm,
            operation=WebhookEventOperation.UPDATE,
            action_by=action_by,
            action_at=datetime.now(timezone.utc),
            resource=WebhookEventResource.USER,
            resource_detail=user_details
        )
        
        assert webhook_event.realm_name == special_realm
        assert webhook_event.resource_detail.first_name == "José"
        assert webhook_event.resource_detail.last_name == "García-López"