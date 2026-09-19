# app/config.py
# SPDX-License-Identifier: GPL-3.0-only

import os
from functools import cached_property, lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.constants import (
    GOCRYPTFS_PASSPHRASE_FILENAME,
    FERNET_ENCRYPTION_KEY_FILENAME,
    VERSITY_ACCESS_KEY_FILENAME,
    VERSITY_SECRET_KEY_FILENAME,
)


class Config(BaseSettings):
    """
    Centralized runtime configuration.

    Combines environment variables, application constants,
    and derived values into a single configuration object.
    """

    INSTALL_SOURCE_CODE: str
    INSTALL_CIPHERDIR: str
    INSTALL_MOUNTPOINT: str
    INSTALL_SECRETS: str
    UVICORN_HOST: str
    UVICORN_PORT: int
    WATCHDOG_INTERVAL_SECONDS: int
    WATCHDOG_LIVENESS_SECONDS: int
    API_PREFIX: str
    LOG_LEVEL: str
    LOG_FORMAT: str
    CORS_ALLOW_ORIGINS: str
    CORS_MAX_AGE_SECONDS: int
    VERSITY_HOST: str
    VERSITY_PORT: int
    VERSITY_WEBGUI_HOST: str
    VERSITY_WEBGUI_PORT: int
    VERSITY_WEBGUI_CORS_ALLOW_ORIGIN: str

    @cached_property
    def GOCRYPTFS_PASSPHRASE_PATH(self) -> str:
        return os.path.join(
            self.INSTALL_SECRETS,
            GOCRYPTFS_PASSPHRASE_FILENAME,
        )

    @cached_property
    def FERNET_ENCRYPTION_KEY_PATH(self) -> str:
        return os.path.join(
            self.INSTALL_SECRETS,
            FERNET_ENCRYPTION_KEY_FILENAME,
        )

    @cached_property
    def VERSITY_ACCESS_KEY_PATH(self) -> str:
        return os.path.join(
            self.INSTALL_SECRETS,
            VERSITY_ACCESS_KEY_FILENAME,
        )

    @cached_property
    def VERSITY_SECRET_KEY_PATH(self) -> str:
        return os.path.join(
            self.INSTALL_SECRETS,
            VERSITY_SECRET_KEY_FILENAME,
        )

    model_config = SettingsConfigDict(
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_config() -> Config:
    return Config()
