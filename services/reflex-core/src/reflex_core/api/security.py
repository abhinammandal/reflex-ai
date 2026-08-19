"""Authentication for local Reflex API clients."""

from secrets import compare_digest
from typing import Annotated

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from reflex_core.infrastructure.api_token import load_or_create_api_token

api_token_header = APIKeyHeader(
    name="X-Reflex-Token",
    auto_error=False,
)


def require_api_token(
    provided_token: Annotated[str | None, Security(api_token_header)],
) -> None:
    expected_token = load_or_create_api_token()

    if provided_token is None or not compare_digest(
        provided_token,
        expected_token,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing Reflex API token.",
        )
