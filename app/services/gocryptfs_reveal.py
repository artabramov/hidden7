# app/services/gocryptfs_reveal.py
# SPDX-License-Identifier: GPL-3.0-only

import logging

from app.config import get_config
from app.errors import UnauthorizedError
from app.locks import LockType, locks
from app.io import read
from app.security.encryption import decrypt_passphrase

log = logging.getLogger(__name__)


async def gocryptfs_reveal(master_password: str) -> str:
    """
    Decrypt and return the stored gocryptfs passphrase using the
    provided master password.
    """
    config = get_config()

    async with locks.lock_directory(
        config.INSTALL_SECRETS,
        LockType.READ,
    ):
        passphrase_encrypted = await read(config.GOCRYPTFS_PASSPHRASE_PATH)

        try:
            passphrase = decrypt_passphrase(
                passphrase_encrypted,
                master_password.encode("utf-8"),
            )

        except ValueError:
            log.warning("msg=passphrase_invalid")
            raise UnauthorizedError

        return passphrase.decode("utf-8")
