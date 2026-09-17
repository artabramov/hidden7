# app/runtime/versity.py
# SPDX-License-Identifier: GPL-3.0-only

from app.config import get_config
from app.constants import (
    VERSITY_ACCESS_KEY_LENGTH,
    VERSITY_SECRET_KEY_LENGTH,
)
from app.io import isfile, read, write
from app.security.randoms import generate_random_string


async def is_versity_created() -> bool:
    """
    Checks whether VersityGW credentials have been created by
    verifying the presence and readability of both credential files.
    """
    config = get_config()

    if not await isfile(config.VERSITY_ACCESS_KEY_PATH):
        return False

    if not await isfile(config.VERSITY_SECRET_KEY_PATH):
        return False

    try:
        access_key = await read(config.VERSITY_ACCESS_KEY_PATH)
        secret_key = await read(config.VERSITY_SECRET_KEY_PATH)
    except Exception:
        return False

    return bool(access_key and secret_key)


async def versity_create() -> None:
    """
    Generate and store VersityGW root credentials.
    """
    config = get_config()

    access_key = generate_random_string(VERSITY_ACCESS_KEY_LENGTH)
    secret_key = generate_random_string(VERSITY_SECRET_KEY_LENGTH)

    await write(
        config.VERSITY_ACCESS_KEY_PATH,
        access_key.encode("utf-8"),
    )
    await write(
        config.VERSITY_SECRET_KEY_PATH,
        secret_key.encode("utf-8"),
    )
