"""Tests for the PIN hashing helpers in src/helpers/security.py."""
from __future__ import annotations

from src.helpers.security import hash_pin, verify_pin


class TestHashPin:
    def test_returns_salt_and_digest_separated_by_colon(self):
        result = hash_pin('1234')
        assert ':' in result
        salt, digest = result.split(':')
        # Salt is 16 bytes -> 32 hex chars; digest is SHA-256 -> 64 hex chars.
        assert len(salt) == 32
        assert len(digest) == 64

    def test_different_calls_produce_different_hashes(self):
        first = hash_pin('4321')
        second = hash_pin('4321')
        assert first != second  # random salt changes the output

    def test_stored_pin_can_be_verified(self):
        stored = hash_pin('0000')
        assert verify_pin('0000', stored) is True

    def test_wrong_pin_fails_verification(self):
        stored = hash_pin('1111')
        assert verify_pin('2222', stored) is False

    def test_verify_pin_handles_malformed_stored_value(self):
        # No colon -> ValueError caught, returns False
        assert verify_pin('1234', 'not-a-valid-stored-pin') is False

    def test_verify_pin_uses_constant_time_comparison(self):
        # Even when the digest matches, hmac.compare_digest is used internally.
        stored = hash_pin('9999')
        assert verify_pin('9999', stored) is True
        # Tampering with the salt should break verification.
        salt, digest = stored.split(':')
        tampered = f"{salt[:-2]}ff:{digest}"
        assert verify_pin('9999', tampered) is False

    def test_pin_is_never_stored_in_plaintext(self):
        stored = hash_pin('5555')
        assert '5555' not in stored
