from typing import Any, List, Optional, Tuple

from openfga_sdk import ClientConfiguration, OpenFgaClient
from openfga_sdk.client import ClientCheckRequest
from openfga_sdk.client.models import (
    ClientBatchCheckItem,
    ClientBatchCheckRequest,
    ClientTuple,
    ClientWriteRequest,
    ClientWriteResponse,
)
from openfga_sdk.credentials import CredentialConfiguration, Credentials

from internal.domains.entities import PermEntity
from internal.infrastructures.external_rebac_authorization_service.abstraction import (
    AbstractExternalReBACAuthorizationSVC,
)


class OpenFGAClient(AbstractExternalReBACAuthorizationSVC):
    def __init__(
        self,
        url: str,
        api_token: str,
        store_id: str,
        authorization_model_id: str,
        timeout_in_millis: Optional[int] = 3000,
    ):
        self._url = url
        self._api_token = api_token
        self._store_id = store_id
        self._authorization_model_id = authorization_model_id
        self._timeout_in_millis = timeout_in_millis

        self._client = OpenFgaClient(
            configuration=ClientConfiguration(
                api_url=self._url,
                store_id=self._store_id,
                authorization_model_id=self._authorization_model_id,
                timeout_millisec=self._timeout_in_millis,
                credentials=Credentials(
                    method="api_token",
                    configuration=CredentialConfiguration(
                        api_token=self._api_token,
                    ),
                ),
            )
        )

    async def create_perms(
        self, entities: List[PermEntity]
    ) -> Tuple[Optional[Any], Optional[Exception]]:
        error: Optional[Exception] = None
        try:
            async with self._client as fga_client:
                writes = [
                    ClientTuple(
                        user=entity.target_obj,
                        relation=entity.relation,
                        object=entity.request_obj,
                    )
                    for entity in entities
                ]
                body = ClientWriteRequest(writes=writes)
                api_response: ClientWriteResponse = await fga_client.write(
                    body=body,
                    options={
                        "authorization_model_id": self._authorization_model_id,
                    },
                )
                await fga_client.close()
                return api_response, None
        except Exception as exc:
            error = exc
            return None, error

    async def check_single_perm(
        self, entity: PermEntity
    ) -> Tuple[Optional[bool], Optional[Exception]]:
        error: Optional[Exception] = None
        try:
            async with self._client as fga_client:
                body = ClientCheckRequest(
                    user=entity.target_obj,
                    relation=entity.relation,
                    object=entity.request_obj,
                )
                response = await fga_client.check(
                    body=body,
                    options={
                        "authorization_model_id": self._authorization_model_id,
                    },
                )
                return response.allowed, None
        except Exception as exc:
            error = exc
            return None, error

    async def check_perms(
        self, entities: List[PermEntity]
    ) -> Tuple[Optional[bool], Optional[Exception]]:
        error: Optional[Exception] = None
        try:
            async with self._client as fga_client:
                checks = [
                    ClientBatchCheckItem(
                        user=entity.target_obj,
                        relation=entity.relation,
                        object=entity.request_obj,
                    )
                    for entity in entities
                ]
                response = await fga_client.batch_check(
                    body=ClientBatchCheckRequest(checks=checks),
                    options={
                        "authorization_model_id": self._authorization_model_id,
                    },
                )
                results = response.result
                for result in results:
                    allowed = result["allowed"]
                    if allowed is False:
                        return False, None

                return True, None
        except Exception as exc:
            error = exc
            return None, error

    async def delete_perms(
        self, entities: List[PermEntity]
    ) -> Tuple[Optional[Any], Optional[Exception]]:
        error: Optional[Exception] = None
        try:
            async with self._client as fga_client:
                deletes = [
                    ClientTuple(
                        user=entity.target_obj,
                        relation=entity.relation,
                        object=entity.request_obj,
                    )
                    for entity in entities
                ]
                body = ClientWriteRequest(deletes=deletes)
                api_response: ClientWriteResponse = await fga_client.write(
                    body=body,
                    options={
                        "authorization_model_id": self._authorization_model_id,
                    },
                )
                await fga_client.close()
                return api_response, None
        except Exception as exc:
            error = exc
            return None, error
