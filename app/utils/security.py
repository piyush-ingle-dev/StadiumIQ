"""Input sanitization helpers.

Every piece of free-text user input (task descriptions, zone names,
chat messages sent for translation) is passed through `clean_text`
before it touches the database or gets echoed back in a template, to
prevent stored/reflected XSS.
"""

from __future__ import annotations

import bleach

# No HTML tags or attributes are allowed anywhere in user input for
# this app; everything is plain text.
_ALLOWED_TAGS: list[str] = []
_ALLOWED_ATTRS: dict[str, list[str]] = {}


def clean_text(value: str | None, max_length: int = 2000) -> str:
    """Strip any HTML/script content from user-supplied text and cap its length.

    Args:
        value: Raw input string, possibly None.
        max_length: Maximum number of characters to keep.

    Returns:
        A sanitized, length-capped string. Empty string if value is None.
    """
    if value is None:
        return ""
    stripped = bleach.clean(value, tags=_ALLOWED_TAGS, attributes=_ALLOWED_ATTRS, strip=True)
    return stripped.strip()[:max_length]


def is_valid_language_code(code: str, supported: list[str]) -> bool:
    """Check whether a language code is one the app supports.

    Args:
        code: Language code to check, e.g. "hi".
        supported: List of supported codes from app config.

    Returns:
        True if the code is supported, False otherwise.
    """
    return code in supported
