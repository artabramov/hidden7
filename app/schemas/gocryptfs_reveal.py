# app/schemas/gocryptfs_reveal.py
# SPDX-License-Identifier: Apache-2.0

from pydantic import BaseModel, ConfigDict, Field

from app.pydantic.master_password import MASTER_PASSWORD_AUTH_DESCRIPTION


class GocryptfsRevealRequest(BaseModel):
    """
    Request schema for revealing stored secrets.

    Authenticates with the existing master password; composition is
    not validated.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    master_password: str = Field(
        description=MASTER_PASSWORD_AUTH_DESCRIPTION,
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
