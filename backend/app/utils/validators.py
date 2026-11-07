import re
from typing import Optional


def is_valid_email(email: str) -> bool:
    pattern = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
    return bool(re.match(pattern, email.lower()))


def is_valid_phone(phone: str) -> bool:
    cleaned = re.sub(r"\s+", "", phone)
    return bool(re.match(r"^\+?[0-9]{10,15}$", cleaned))


def is_valid_password(password: str) -> bool:
    if len(password) < 8:
        return False
    has_letter = bool(re.search(r"[a-zA-Z]", password))
    has_digit = bool(re.search(r"\d", password))
    return has_letter and has_digit


def sanitize_text(text: Optional[str], max_length: int = 5000) -> Optional[str]:
    """Strip and truncate input text."""
    if not text:
        return None
    return text.strip()[:max_length]


def is_valid_language(lang: str) -> bool:
    return lang in {"en", "ta", "hi", "te"}
