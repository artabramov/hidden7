# app/runtime/versity.py
# SPDX-License-Identifier: GPL-3.0-only

import asyncio
import logging
import os
import signal

from app.constants import (
    VERSITY_ACCESS_KEY_LENGTH,
    VERSITY_SECRET_KEY_LENGTH,
)
from app.errors import InternalServerError
from app.io import isfile, read, write
from app.security.randoms import generate_random_string

log = logging.getLogger(__name__)


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


async def versity_start(
    host: str,
    port: int,
    webgui_host: str,
    webgui_port: int,
    webgui_gateway: str,
    webgui_cors_allow_origin: str,
    mountpoint: str,
    access_key: str,
    secret_key: str,
) -> None:
    """
    Start VersityGW using the provided root credentials and POSIX
    storage directory.
    """
    env = os.environ.copy()
    env["ROOT_ACCESS_KEY"] = access_key
    env["ROOT_SECRET_KEY"] = secret_key

    try:
        await asyncio.create_subprocess_exec(
            "versitygw",
            "--port",
            f"{host}:{port}",
            "--webui",
            f"{webgui_host}:{webgui_port}",
            "--webui-gateways",
            webgui_gateway,
            "--cors-allow-origin",
            webgui_cors_allow_origin,
            "posix",
            mountpoint,
            env=env,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
    except Exception:
        log.exception("msg=versity_start_failed")
        raise InternalServerError


def _get_versity_pid() -> int | None:
    for entry in os.scandir("/proc"):
        if not entry.name.isdigit():
            continue

        try:
            with open(
                os.path.join(entry.path, "comm"),
                "r",
                encoding="utf-8",
            ) as file:
                if file.read().strip() == "versitygw":
                    return int(entry.name)
        except (FileNotFoundError, PermissionError, ProcessLookupError):
            continue

    return None


async def is_versity_running() -> bool:
    """
    Check whether a VersityGW process is currently running.
    """
    return _get_versity_pid() is not None


async def versity_stop() -> None:
    """
    Stop the running VersityGW process.
    """
    pid = _get_versity_pid()
    if pid is None:
        return

    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
