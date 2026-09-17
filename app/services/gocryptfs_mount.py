# app/services/gocryptfs_mount.py
# SPDX-License-Identifier: GPL-3.0-only

import logging

from app.config import get_config
from app.errors import UnauthorizedError
from app.locks import LockType, locks
from app.io import isdir, mktree, read
from app.runtime.cipherdir import cipherdir_mount
from app.security.encryption import decrypt_passphrase

log = logging.getLogger(__name__)


# TODO: Add garbage cleaning (removal of possible file system artifacts)
# when cipherdir mounting.

async def gocryptfs_mount(master_password: str) -> None:
    """
    Mount the encrypted storage by decrypting the stored passphrase
    with the master password, mounting the gocryptfs filesystem,
    ensuring mountpoint directories exist (db, buckets, tmp),
    creating ORM tables if missing, and checking database integrity.
    If a post-mount step fails, the mount is rolled back.
    """
    config = get_config()

    async with locks.lock_directory(
        config.INSTALL_SECRETS,
        LockType.WRITE,
    ):
        passphrase_encrypted = await read(config.GOCRYPTFS_PASSPHRASE_PATH)

        try:
            passphrase_bytes = decrypt_passphrase(
                passphrase_encrypted,
                master_password.encode("utf-8"),
            )

        except ValueError:
            log.warning("msg=passphrase_invalid")
            raise UnauthorizedError

        if not await isdir(config.INSTALL_MOUNTPOINT):
            await mktree(config.INSTALL_MOUNTPOINT)

        await cipherdir_mount(
            passphrase=passphrase_bytes.decode("utf-8"),
            cipherdir=config.INSTALL_CIPHERDIR,
            mountpoint=config.INSTALL_MOUNTPOINT,
        )
