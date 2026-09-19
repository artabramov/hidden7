# app/constants.py
# SPDX-License-Identifier: GPL-3.0-only

HIDDEN_TITLE = "Hidden — S3-compatible storage secured by gocryptfs"

GOCRYPTFS_PASSPHRASE_LENGTH = 80
GOCRYPTFS_PASSPHRASE_FILENAME = "gocryptfs_passphrase.enc"

WATCHDOG_HEARTBEAT_PATH = "/tmp/gocryptfs-watchdog.touch"

FERNET_ENCRYPTION_KEY_FILENAME = "fernet_encryption.key"

FILE_CHUNK_SIZE_BYTES = 1024 * 64
FILE_MIMETYPE_READ_BYTES = 1024 * 16

VERSITY_ACCESS_KEY_LENGTH = 20
VERSITY_ACCESS_KEY_FILENAME = "versity_access.key"

VERSITY_SECRET_KEY_LENGTH = 40
VERSITY_SECRET_KEY_FILENAME = "versity_secret.key"

VERSITY_DATA_DIRNAME = "data"
VERSITY_IAM_DIRNAME = "iam"
