# app/pydantic/master_password.py
# SPDX-License-Identifier: Apache-2.0


def validate_master_password(value: str) -> str:
    """
    Validate that the master password contains at least one lowercase
    letter, one uppercase letter, and one digit.
    """
    if not any(c.islower() for c in value):
        raise ValueError(
            "Master password must contain a lowercase letter."
        )
    if not any(c.isupper() for c in value):
        raise ValueError(
            "Master password must contain an uppercase letter."
        )
    if not any(c.isdigit() for c in value):
        raise ValueError(
            "Master password must contain a digit."
        )
    return value
