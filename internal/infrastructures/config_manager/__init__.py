import asyncio
import hashlib
import json
from typing import Dict, List, Optional, Tuple

from consul.aio import Consul
from dependency_injector import containers

from config import AppConfig
from utils.logger_utils import get_shared_logger


class ConfigManager:
    def __init__(
        self,
        di_container: containers.DeclarativeContainer,
        app_config: AppConfig,
        address: str,
        token: str,
        env: str,
        interval: int = 10,
        static_keys: Optional[List[str]] = None,
    ):
        host, port = address.split(":") if ":" in address else (address, 8500)
        self.consul = Consul(host=host, port=int(port), token=token or None)

        self._env = f"{env}/" if env and not env.endswith("/") else env
        self._interval = interval
        self._logger = get_shared_logger()
        self._static_keys = static_keys or []
        self._hash = {}
        self._config_cache = {}
        self._running = False
        self._di_container = di_container
        self._app_config = app_config

    async def load(self) -> Optional[Exception]:
        _, err = await self.get_all()
        if err:
            return err

        self._running = True
        asyncio.create_task(self._reload_kv())
        return None

    async def get_all(self) -> Tuple[bool, Optional[Exception]]:
        try:
            index, pairs = await self.consul.kv.get(self._env, recurse=True)
            changed = 0

            if pairs:
                for pair in pairs:
                    key = (
                        pair["Key"].replace(self._env, "", 1).lower().replace("__", ".")
                    )
                    if key in self._static_keys:
                        continue

                    value = pair["Value"]
                    if value is None:
                        continue

                    new_hash = self._generate_sha512_hash(value)
                    if self._hash.get(key, "") != new_hash:
                        self._config_cache[key] = value.decode("utf-8")
                        self._hash[key] = new_hash
                        changed += 1

            if changed > 0:
                self._logger.info(
                    f"ConfigManager reload config, {changed} keys changed"
                )
            self._logger.debug("ConfigManager load keys - finish")
            return (changed > 0), None
        except Exception as exc:
            self._logger.error(f"Error loading keys: {exc}")
            return False, exc

    async def get_config(self, key: str) -> Optional[str]:
        normalized_key = key.lower().replace("__", ".")
        if normalized_key in self._config_cache:
            return self._config_cache[normalized_key]

        try:
            full_key = f"{self._env}{key}"
            _, data = await self.consul.kv.get(full_key)
            if data and data["Value"]:
                value = data["Value"].decode("utf-8")
                self._config_cache[normalized_key] = value
                self._hash[normalized_key] = self._generate_sha512_hash(data["Value"])
                return value
            return None
        except Exception as exc:
            self._logger.error(f"Error fetching key '{key}': {exc}")
            return None

    async def _reload_kv(self):
        while self._running:
            await asyncio.sleep(self._interval)
            changed, err = await self.get_all()
            if err:
                self._logger.error(str(err))
            elif changed and self._app_config and self._di_container:
                self._logger.debug("Detected config change — updating AppConfig...")
                await self.update_app_config()

    def _generate_sha512_hash(self, data: bytes) -> str:
        return hashlib.sha512(data).hexdigest()

    async def update_app_config(self) -> AppConfig:
        for field_name, field_info in self._app_config.model_fields.items():
            alias = field_info.alias or field_name
            value = await self.get_config(alias)

            if value is not None:
                try:
                    field_type = field_info.annotation

                    if field_type in [str, Optional[str]]:
                        setattr(self._app_config, field_name, str(value))
                    elif field_type in [int, Optional[int]]:
                        setattr(self._app_config, field_name, int(value))
                    elif field_type in [float, Optional[float]]:
                        setattr(self._app_config, field_name, float(value))
                    elif field_type in [bool, Optional[bool]]:
                        setattr(self._app_config, field_name, value.lower() == "true")
                    elif field_type in [dict, Optional[dict], Optional[Dict]]:
                        try:
                            setattr(self._app_config, field_name, json.loads(value))
                        except json.JSONDecodeError:
                            self._logger.error(
                                f"Invalid JSON for {field_name}: {value}"
                            )
                    else:
                        setattr(self._app_config, field_name, value)
                except Exception as exc:
                    self._logger.error(f"Failed to parse {field_name}={value}: {exc}")

        self._di_container.config.override(self._app_config.model_dump())
        self._logger.info("AppConfig updated with values from ConfigManager")
        return self._app_config
