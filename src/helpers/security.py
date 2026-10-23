import hashlib
import hmac
import os

_ITERATIONS = 200_000


def hash_pin(pin: str) -> str:
    """Return 'salt:hash' (both hex). The PIN itself is never stored."""
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", pin.encode(), salt, _ITERATIONS)
    return f"{salt.hex()}:{digest.hex()}"


def verify_pin(pin: str, stored: str) -> bool:
    """Check a typed PIN against a stored 'salt:hash' string."""
    try:
        salt_hex, digest_hex = stored.split(":")
        digest = hashlib.pbkdf2_hmac(
            "sha256", pin.encode(), bytes.fromhex(salt_hex), _ITERATIONS
        )
    except ValueError:
        return False
    return hmac.compare_digest(digest.hex(), digest_hex)
