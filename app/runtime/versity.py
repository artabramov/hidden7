# app/runtime/versity.py
# SPDX-License-Identifier: GPL-3.0-only

from app.constants import (
    VERSITY_ACCESS_KEY_LENGTH,
    VERSITY_SECRET_KEY_LENGTH,
)
from app.io import isfile, read, write
from app.security.randoms import generate_random_string


async def is_versity_created(
    access_key_path: str,
    secret_key_path: str,
) -> bool:
    """
    Checks whether VersityGW credentials have been created by
    verifying the presence and readability of both credential files.
    """
    if not await isfile(access_key_path):
        return False

    if not await isfile(secret_key_path):
        return False

    try:
        access_key = await read(access_key_path)
        secret_key = await read(secret_key_path)
    except Exception:
        return False

    return bool(access_key and secret_key)


async def versity_create(
    access_key_path: str,
    secret_key_path: str,
) -> None:
    """
    Generate and store VersityGW root credentials.
    """
    access_key = generate_random_string(VERSITY_ACCESS_KEY_LENGTH)
    secret_key = generate_random_string(VERSITY_SECRET_KEY_LENGTH)

    await write(
        access_key_path,
        access_key.encode("utf-8"),
    )

    await write(
        secret_key_path,
        secret_key.encode("utf-8"),
    )
