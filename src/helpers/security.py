"""
Security utilities for PIN hashing and verification.
Uses PBKDF2-HMAC-SHA256 for secure password/PIN storage.
"""

import hashlib
import hmac
import os

_ITERATIONS = 200_000


def hash_pin(pin: str) -> str:
    """
    Hash a PIN using PBKDF2-HMAC-SHA256.

    Args:
        pin: The 4-digit PIN to hash.

    Returns:
        A string in format 'salt:hash' (both hex encoded).
        The PIN itself is never stored.
    """
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac('sha256', pin.encode(), salt, _ITERATIONS)
    return f"{salt.hex()}:{digest.hex()}"


def verify_pin(pin: str, stored: str) -> bool:
    """
    Verify a typed PIN against a stored hash.

    Args:
        pin: The PIN entered by the user.
        stored: Stored hash string in format 'salt:hash'.

    Returns:
        True if the PIN matches, False otherwise.
    """
    try:
        salt_hex, digest_hex = stored.split(':')
        digest = hashlib.pbkdf2_hmac(
            'sha256', pin.encode(), bytes.fromhex(salt_hex), _ITERATIONS
        )
    except ValueError:
        return False
    return hmac.compare_digest(digest.hex(), digest_hex)
