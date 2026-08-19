"""Manage the secret token used by local Reflex clients."""

from secrets import token_urlsafe

from reflex_core.infrastructure.database import DATA_DIRECTORY

TOKEN_PATH = DATA_DIRECTORY / "api-token"


def load_or_create_api_token() -> str:
    DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)

    try:
        token = TOKEN_PATH.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        token = token_urlsafe(32)

        try:
            TOKEN_PATH.write_text(token, encoding="utf-8")
        except OSError as exc:
            raise RuntimeError("Reflex could not save its local API token.") from exc

    if not token:
        raise RuntimeError("The local Reflex API token is empty.")

    return token
