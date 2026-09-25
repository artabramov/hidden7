# app/schemas/gocryptfs_unmount.py
# SPDX-License-Identifier: Apache-2.0

from pydantic import BaseModel, ConfigDict, Field

from app.pydantic.master_password import MASTER_PASSWORD_AUTH_DESCRIPTION


class GocryptfsUnmountRequest(BaseModel):
    """
    Request schema for unmounting encrypted storage.

    Authenticates with the existing master password; composition is
    not validated.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    master_password: str = Field(
        description=MASTER_PASSWORD_AUTH_DESCRIPTION,
    )
