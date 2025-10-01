"""Input validation helpers for domain data.

Provides simple, reusable validators for non-empty strings, age values, and
email addresses. Errors are raised as :class:`ValueError` with descriptive
messages suitable for display in UI layers.
"""

import re

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def validate_non_empty(val: str, fld: str):
    """Validate a non-empty trimmed string.

    :param val: Value to check.
    :type val: str
    :param fld: Field name for error messages.
    :type fld: str
    :return: Trimmed value.
    :rtype: str
    :raises ValueError: If empty or not a string.
    """
    if not isinstance(val, str) or not val.strip():
        raise ValueError(f"{fld} must be a non-empty string")
    return val.strip()

def validate_age(ag: int):
    """Validate that an age is a non-negative integer.

    :param ag: Age value.
    :type ag: int
    :return: Same value if valid.
    :rtype: int
    :raises ValueError: If invalid.
    """
    if not isinstance(ag, int) or ag < 0:
        raise ValueError("age must be a non-negative integer")
    return ag

def validate_email(em: str):
    """Validate an email address format.

    Uses a minimal regex that enforces a single ``@`` and a dot domain.

    :param em: Email string.
    :type em: str
    :return: Normalized email.
    :rtype: str
    :raises ValueError: If not matching the expected pattern.
    """
    em = em.strip()
    if not EMAIL_RE.match(em):
        raise ValueError("email must be of the form something@domain.tld")
    return em