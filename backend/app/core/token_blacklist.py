"""
Token blacklist.

Stores invalidated JTI (JWT IDs) so logged-out tokens
cannot be reused. Backed by an in-memory set for now;
swap for Redis in Phase 13.
"""

_blacklist: set[str] = set()


def blacklist_token(jti: str) -> None:
    _blacklist.add(jti)


def is_blacklisted(jti: str) -> bool:
    return jti in _blacklist
