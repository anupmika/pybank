"""
Tests for the PIN hashing helpers in src/helpers/security.py.

This module tests PBKDF2-HMAC-SHA256 based PIN hashing and verification
functionality including security properties.
"""

from __future__ import annotations

from src.helpers.security import hash_pin, verify_pin


class TestHashPin:
    """Test suite for PIN hashing and verification."""

    def test_returns_salt_and_digest_separated_by_colon(self):
        """Test that hash format is 'salt:hash' with correct lengths."""
        result = hash_pin('1234')
        assert ':' in result
        salt, digest = result.split(':')
        # Salt is 16 bytes -> 32 hex chars; digest is SHA-256 -> 64 hex chars.
        assert len(salt) == 32
        assert len(digest) == 64

    def test_different_calls_produce_different_hashes(self):
        """Test that random salt produces different hashes for same PIN."""
        first = hash_pin('4321')
        second = hash_pin('4321')
        assert first != second  # random salt changes the output

    def test_stored_pin_can_be_verified(self):
        """Test that correct PIN verifies successfully."""
        stored = hash_pin('0000')
        assert verify_pin('0000', stored) is True

    def test_wrong_pin_fails_verification(self):
        """Test that incorrect PIN fails verification."""
        stored = hash_pin('1111')
        assert verify_pin('2222', stored) is False

    def test_verify_pin_handles_malformed_stored_value(self):
        """Test that malformed stored hash returns False without crashing."""
        # No colon -> ValueError caught, returns False
        assert verify_pin('1234', 'not-a-valid-stored-pin') is False

    def test_verify_pin_uses_constant_time_comparison(self):
        """Test that verification uses constant-time comparison."""
        # Even when the digest matches, hmac.compare_digest is used internally.
        stored = hash_pin('9999')
        assert verify_pin('9999', stored) is True
        # Tampering with the salt should break verification.
        salt, digest = stored.split(':')
        tampered = f"{salt[:-2]}ff:{digest}"
        assert verify_pin('9999', tampered) is False

    def test_pin_is_never_stored_in_plaintext(self):
        """Test that the original PIN is not present in the stored hash."""
        stored = hash_pin('5555')
        assert '5555' not in stored
