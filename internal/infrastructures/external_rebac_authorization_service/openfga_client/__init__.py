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

    async def create_perms(self, entities: List[PermEntity]) -> List[dict]:
        results = []
        writes = [
            ClientTuple(
                user=entity.target_obj,
                relation=entity.relation,
                object=entity.request_obj,
            )
            for entity in entities
        ]
        body = ClientWriteRequest(writes=writes)
        api_response: ClientWriteResponse = await self._client.write(
            body=body,
            options={
                "authorization_model_id": self._authorization_model_id,
            },
        )
        for res in api_response.writes:
            results.append(
                {
                    "success": res.success,
                    "error": res.error,
                }
            )

        return results

    async def check_single_perm(self, entity: PermEntity) -> bool:
        body = ClientCheckRequest(
            user=entity.target_obj,
            relation=entity.relation,
            object=entity.request_obj,
        )
        response = await self._client.check(
            body=body,
            options={
                "authorization_model_id": self._authorization_model_id,
            },
        )
        return response.allowed

    async def check_perms(self, entities: List[PermEntity]) -> bool:
        checks = [
            ClientBatchCheckItem(
                user=entity.target_obj,
                relation=entity.relation,
                object=entity.request_obj,
            )
            for entity in entities
        ]
        response = await self._client.batch_check(
            body=ClientBatchCheckRequest(checks=checks),
            options={
                "authorization_model_id": self._authorization_model_id,
            },
        )
        results = response.result
        for result in results:
            allowed = result["allowed"]
            if allowed is False:
                return False

        return True

    async def delete_perms(self, entities: List[PermEntity]) -> List[dict]:
        results = []
        deletes = [
            ClientTuple(
                user=entity.target_obj,
                relation=entity.relation,
                object=entity.request_obj,
            )
            for entity in entities
        ]
        body = ClientWriteRequest(deletes=deletes)
        api_response: ClientWriteResponse = await self._client.write(
            body=body,
            options={
                "authorization_model_id": self._authorization_model_id,
            },
        )
        for res in api_response.deletes:
            results.append(
                {
                    "success": res.success,
                    "error": str(res.error),
                }
            )
        return results

    async def close(self):
        await self._client.close()
