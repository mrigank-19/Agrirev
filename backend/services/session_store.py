"""In-memory conversation state, keyed by phone number.

Tracks where each farmer is in the sequential Q&A flow. Matches the spec's
note that this can later be swapped for Firebase without changing callers.
"""

_sessions: dict[str, dict] = {}


def get_session(phone_number: str) -> dict | None:
    return _sessions.get(phone_number)


def create_session(phone_number: str) -> dict:
    session = {"step": "district"}
    _sessions[phone_number] = session
    return session


def update_session(phone_number: str, session: dict) -> None:
    _sessions[phone_number] = session


def reset_session(phone_number: str) -> None:
    _sessions.pop(phone_number, None)
