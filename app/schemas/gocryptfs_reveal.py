# app/schemas/gocryptfs_reveal.py
# SPDX-License-Identifier: GPL-3.0-only

from pydantic import BaseModel, ConfigDict, Field


class GocryptfsRevealRequest(BaseModel):
    """
    Request schema for revealing the stored gocryptfs passphrase
    with the master password.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    master_password: str = Field(
        description="Master password used to decrypt the passphrase.",
    )


class GocryptfsRevealResponse(BaseModel):
    """
    Response schema containing the decrypted gocryptfs passphrase
    and VersityGW root credentials.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    gocryptfs_passphrase: str = Field(
        description="Decrypted gocryptfs passphrase.",
    )

    versity_access_key: str = Field(
        description="VersityGW root access key.",
    )

    versity_secret_key: str = Field(
        description="VersityGW root secret key.",
    )
