# app/schemas/gocryptfs_reset.py
# SPDX-License-Identifier: GPL-3.0-only

from pydantic import BaseModel, ConfigDict, Field


class GocryptfsResetRequest(BaseModel):
    """
    Request schema for resetting the encrypted storage requiring
    the master password for authorization.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    master_password: str = Field(
        description="Master password used to authorize storage reset.",
    )
