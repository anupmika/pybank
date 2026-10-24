"""
Tests for CLI utilities.
"""

from __future__ import annotations

from src.utils.cli_utils import colored


class TestCLIUtils:
    """Test CLI utility functions."""

    def test_colored_with_valid_color(self, capsys):
        """Test colored function with valid color."""
        result = colored('Hello', 'red')
        assert 'Hello' in result
        captured = capsys.readouterr()
        assert 'Hello' in captured.out

    def test_colored_with_invalid_color(self, capsys):
        """Test colored function with invalid color falls back."""
        result = colored('Hello', 'notacolor')
        assert 'Hello' in result

    def test_colored_case_insensitive(self, capsys):
        """Test colored function is case insensitive."""
        result = colored('Hello', 'GREEN')
        assert 'Hello' in result
