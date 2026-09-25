# app/constants.py
# SPDX-License-Identifier: Apache-2.0

HIDDEN_TITLE = "Hidden — S3-compatible storage secured by gocryptfs"

GOCRYPTFS_PASSPHRASE_LENGTH = 80
GOCRYPTFS_PASSPHRASE_FILENAME = "gocryptfs_passphrase.enc"

WATCHDOG_HEARTBEAT_PATH = "/tmp/gocryptfs-watchdog.touch"

FERNET_ENCRYPTION_KEY_FILENAME = "fernet_encryption.key"

VERSITY_ACCESS_KEY_LENGTH = 20
VERSITY_ACCESS_KEY_FILENAME = "versity_access.key"

VERSITY_SECRET_KEY_LENGTH = 40
VERSITY_SECRET_KEY_FILENAME = "versity_secret.key"

VERSITY_DATA_DIRNAME = "data"
VERSITY_IAM_DIRNAME = "iam"
