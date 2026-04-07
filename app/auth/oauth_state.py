import secrets
import uuid
from typing import Dict, Optional, Set

# Login flow — state is just a CSRF nonce, not tied to a user yet
_login_nonces: Set[str] = set()

# Connected account flow (e.g. Google Drive) — state maps to an existing user
_state_store: Dict[str, uuid.UUID] = {}


def create_login_nonce() -> str:
    nonce = secrets.token_urlsafe(32)
    _login_nonces.add(nonce)
    return nonce


def consume_login_nonce(nonce: str) -> bool:
    if nonce in _login_nonces:
        _login_nonces.discard(nonce)
        return True
    return False


def create_state(user_id: uuid.UUID) -> str:
    token = secrets.token_urlsafe(32)
    _state_store[token] = user_id
    return token


def consume_state(state: str) -> Optional[uuid.UUID]:
    """Returns the user_id and removes the state entry. Returns None if not found."""
    return _state_store.pop(state, None)
