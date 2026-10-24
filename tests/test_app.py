"""
Tests for the main application loop.
"""

from __future__ import annotations

from unittest.mock import patch

from src import app


class TestApp:
    """Test application loop."""

    def test_app_close_on_choice_8(self, capsys):
        """Test app exits when choice 8 is selected."""
        with patch('builtins.input', return_value='8'):
            app.bank()
        captured = capsys.readouterr()
        assert 'Exiting' in captured.out

    def test_app_invalid_choice(self, capsys):
        """Test app handles invalid choice."""
        # First invalid, then exit
        with patch('builtins.input', side_effect=['99', '8']):
            app.bank()
        captured = capsys.readouterr()
        assert 'Invalid Choice' in captured.out

    def test_app_all_menu_options(self, capsys):
        """Test all menu options in app loop."""
        # We'll test each option briefly

        # For now just test a few key paths
