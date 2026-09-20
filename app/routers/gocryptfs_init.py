# app/routers/gocryptfs_init.py
# SPDX-License-Identifier: GPL-3.0-only

from fastapi import APIRouter, Depends, Response, status

from app.dependencies.require_gocryptfs import require_gocryptfs
from app.schemas.gocryptfs_init import (
    GocryptfsInitRequest,
    GocryptfsInitResponse,
)
from app.services.gocryptfs_init import gocryptfs_init

router = APIRouter(tags=["gocryptfs"])


@router.post(
    "/gocryptfs/init",
    responses={
        422: {
            "description": (
                "Request body failed basic Pydantic validation. "
                "This includes type validation, field constraints, "
                "and custom validators."
            ),
        },
        502: {
            "description": (
                "Gocryptfs infrastructure is in a conflicting state: "
                "cipherdir is already initialized, already mounted, "
                "or required secrets already exist."
            ),
        },
    },
    response_model=GocryptfsInitResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_gocryptfs(
        require_cipherdir=False,
        require_mountpoint=False,
        require_passphrase=False,
    ))],
    summary="Initialize gocryptfs cipherdir (on first boot).",
)
async def gocryptfs_init_router(
    data: GocryptfsInitRequest,
) -> Response:
    """
    Initializes encrypted application storage. It generates a strong
    random gocryptfs passphrase, encrypts it with the provided master
    password, and initializes the cipherdir. It also creates internal
    application keys and VersityGW root credentials.

    This endpoint is intended for one-time initialization immediately
    after installation.

    `GOCRYPTFS_INITIALIZED` — hook executed after the gocryptfs
    cipherdir is successfully initialized.
    """
    access_key, secret_key = await gocryptfs_init(
        data.master_password,
    )

    return GocryptfsInitResponse(
        access_key=access_key,
        secret_key=secret_key,
    )
